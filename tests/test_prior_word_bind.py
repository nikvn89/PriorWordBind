"""Deterministic tests for the exact PriorWordBind contract source.

The fake SDK exercises validation order, state transitions, prompt boundaries,
and accounting. It does not simulate GenVM consensus or prove model semantics.
"""

from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import types
import unittest


SOURCE = Path(
    os.environ.get(
        "PRIOR_WORD_BIND_SOURCE",
        Path(__file__).parents[1] / "contracts" / "PriorWordBind.py",
    )
)

PRIMARY = "0x3065E31B1D993d7C0D59E6786844cBa56780B2d3"
COUNTERPART = "0x5a52d040581A76e2C032542855D31480f2ea7097"
OUTSIDER = "0x1111111111111111111111111111111111111111"

TOPIC = "Release audit publication"
BASELINE = "We will publish the audit report for every release."
KEEPS = "The scope remains unchanged across all covered occasions."
NARROWS = "The later text reaches fewer covered occasions."


class UserError(Exception):
    pass


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


class U256(int):
    def __new__(cls, value):
        value = int(value)
        if not 0 <= value < 2**256:
            raise ValueError("test u256 bounds")
        return super().__new__(cls, value)


class TreeMap(dict):
    def __getitem__(self, key):
        return copy.deepcopy(super().__getitem__(key))

    def get(self, key, default=None):
        return copy.deepcopy(super().get(key, default))


class Hash:
    def __init__(self, data):
        # Equality/isolation stand-in only. This does not claim to validate the
        # SDK Keccak implementation or a StudioNet position id.
        self._hash = hashlib.sha256(data)

    def hexdigest(self):
        return self._hash.hexdigest()


class Runtime:
    def __init__(self):
        self.outputs = []
        self.default = {"outcome": "KEEPS_PRIOR"}
        self.prompts = []
        self.consensus_calls = 0
        self.validator_results = []

    def exec_prompt(self, prompt, response_format):
        if response_format != "json":
            raise AssertionError("unexpected response format")
        self.prompts.append(prompt)
        value = self.outputs.pop(0) if self.outputs else self.default
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)

    def run(self, leader, validator):
        self.consensus_calls += 1
        leader_result = Return(leader())
        agreed = validator(leader_result)
        self.validator_results.append(agreed)
        if not agreed:
            raise UserError("Fake consensus did not converge")
        return leader_result


def load_contract():
    runtime = Runtime()
    gl = types.SimpleNamespace(
        Contract=object,
        public=types.SimpleNamespace(
            write=lambda fn: fn,
            view=lambda fn: fn,
        ),
        message=types.SimpleNamespace(sender_address=PRIMARY),
        vm=types.SimpleNamespace(
            UserError=UserError,
            Return=Return,
            run_nondet_unsafe=runtime.run,
        ),
        nondet=types.SimpleNamespace(exec_prompt=runtime.exec_prompt),
    )

    sdk = types.ModuleType("genlayer")
    exports = {
        "gl": gl,
        "u256": U256,
        "TreeMap": TreeMap,
        "Address": str,
        "allow_storage": lambda cls: cls,
        "Keccak256": Hash,
    }
    for name, value in exports.items():
        setattr(sdk, name, value)
    sys.modules["genlayer"] = sdk

    module = types.ModuleType("prior_word_bind_under_test")
    sys.modules[module.__name__] = module
    source = SOURCE.read_text(encoding="utf-8")
    exec(compile(source, str(SOURCE), "exec"), module.__dict__)

    contract = module.PriorWordBind()
    for name in (
        "positions",
        "followups",
        "followup_index",
        "reliance_label",
        "reliance_active",
        "reliance_index",
    ):
        setattr(contract, name, TreeMap())
    return module, contract, gl, runtime


class PriorWordBindTests(unittest.TestCase):
    def setUp(self):
        self.module, self.contract, self.gl, self.runtime = load_contract()

    def sender(self, address):
        self.gl.message.sender_address = address

    def open(self, topic=TOPIC, text=BASELINE):
        self.contract.open_position(topic, text)
        return self.contract._position_id_for(PRIMARY, topic.strip())

    def set_position(self, pid, **changes):
        position = self.contract.positions[pid]
        for key, value in changes.items():
            setattr(position, key, value)
        self.contract.positions[pid] = position

    def snapshot(self):
        return copy.deepcopy(vars(self.contract))

    def refuse(self, call, message, model_delta=0):
        before = self.snapshot()
        before_calls = self.runtime.consensus_calls
        with self.assertRaisesRegex(Exception, message):
            call()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(
            before_calls + model_delta,
            self.runtime.consensus_calls,
        )

    def test_open_position_stores_immutable_initial_state(self):
        pid = self.open()
        position = self.contract.get_position(pid)
        self.assertEqual(position["creator"], PRIMARY)
        self.assertEqual(position["topic"], TOPIC)
        self.assertEqual(position["position_text"], BASELINE)
        self.assertEqual(position["state"], "STANDING")
        self.assertEqual(position["followup_count"], 0)
        self.assertEqual(position["model_calls"], 0)
        self.assertEqual(position["reliance_count"], 0)
        self.assertEqual(position["standing_reliance_count"], 0)

    def test_position_id_is_creator_and_trimmed_topic_scoped(self):
        self.contract.open_position("  " + TOPIC + "  ", BASELINE)
        pid = self.contract._position_id_for(PRIMARY, TOPIC)
        self.assertNotEqual(self.contract.get_position(pid), {})

        self.sender(OUTSIDER)
        self.contract.open_position(TOPIC, BASELINE)
        other = self.contract._position_id_for(OUTSIDER, TOPIC)
        self.assertNotEqual(pid, other)

    def test_duplicate_position_is_refused(self):
        self.open()
        self.refuse(
            lambda: self.contract.open_position(" " + TOPIC + " ", BASELINE),
            "Position already exists",
        )

    def test_empty_and_oversized_position_inputs_are_refused(self):
        for call, message in (
            (lambda: self.contract.open_position("", BASELINE), "Topic cannot"),
            (lambda: self.contract.open_position("x" * 81, BASELINE), "Topic is too long"),
            (lambda: self.contract.open_position(TOPIC, " "), "Position text cannot"),
            (lambda: self.contract.open_position(TOPIC, "x" * 601), "Position text is too long"),
        ):
            with self.subTest(message=message):
                self.refuse(call, message)

    def test_reserved_tokens_are_case_insensitively_refused_at_ingress(self):
        cases = (
            ("topic " + self.module.TOPIC_OPEN.lower(), BASELINE),
            (TOPIC, "text " + self.module.NARROWS_PRIOR.lower()),
        )
        for topic, text in cases:
            with self.subTest(topic=topic):
                self.refuse(
                    lambda topic=topic, text=text: self.contract.open_position(
                        topic,
                        text,
                    ),
                    "Reserved prompt token",
                )

    def test_safe_prompt_filter_reaches_a_fixed_point(self):
        nested = "<<UNTRUSTED_TOPIC>UNTRUSTED_TOPIC>"
        cleaned = self.contract._safe_prompt_text(nested)
        self.assertNotIn(self.module.TOPIC_OPEN, cleaned.upper())

    def test_reliance_registration_is_permissionless(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "Counterparty")

        position = self.contract.get_position(pid)
        reliance = self.contract.get_reliance(pid, COUNTERPART)
        self.assertEqual(position["reliance_count"], 1)
        self.assertEqual(position["standing_reliance_count"], 1)
        self.assertEqual(reliance["label"], "Counterparty")
        self.assertTrue(reliance["active"])

    def test_creator_may_register_own_reliance(self):
        pid = self.open()
        self.contract.register_reliance(pid, "Self-record")
        self.assertTrue(
            self.contract.get_reliance(pid, PRIMARY)["active"]
        )

    def test_duplicate_reliance_is_refused(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "First")
        self.refuse(
            lambda: self.contract.register_reliance(pid, "Second"),
            "Wallet already registered",
        )

    def test_relier_label_validation_is_deterministic(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.refuse(
            lambda: self.contract.register_reliance(pid, ""),
            "Relier label cannot",
        )
        self.refuse(
            lambda: self.contract.register_reliance(pid, "x" * 81),
            "Relier label is too long",
        )

    def test_reliance_cap_is_position_scoped(self):
        pid = self.open()
        self.set_position(
            pid,
            reliance_count=self.module.u256(50),
        )
        self.sender(COUNTERPART)
        self.refuse(
            lambda: self.contract.register_reliance(pid, "Counterparty"),
            "Reliance limit reached",
        )

    def test_withdrawal_does_not_exist_while_position_stands(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "Counterparty")
        self.refuse(
            lambda: self.contract.withdraw_reliance(pid),
            "Position is still standing",
        )

    def test_only_author_may_submit_and_no_model_is_touched(self):
        pid = self.open()
        self.sender(OUTSIDER)
        self.refuse(
            lambda: self.contract.submit_followup(pid, KEEPS),
            "Only the position author",
        )

    def test_keeps_followup_is_recorded_without_locking(self):
        pid = self.open()
        self.runtime.default = {"outcome": "KEEPS_PRIOR"}
        self.contract.submit_followup(pid, KEEPS)

        position = self.contract.get_position(pid)
        entries = self.contract.get_followups(pid, 0, 10)
        self.assertEqual(position["state"], "STANDING")
        self.assertEqual(position["followup_count"], 1)
        self.assertEqual(position["model_calls"], 1)
        self.assertEqual(entries[0]["outcome"], "KEEPS_PRIOR")
        self.assertEqual(self.runtime.consensus_calls, 1)

    def test_narrows_followup_permanently_walks_back_position(self):
        pid = self.open()
        self.runtime.default = {"outcome": "NARROWS_PRIOR"}
        self.contract.submit_followup(pid, NARROWS)

        position = self.contract.get_position(pid)
        entries = self.contract.get_followups(pid, 0, 10)
        self.assertEqual(position["state"], "WALKED_BACK")
        self.assertEqual(position["model_calls"], 1)
        self.assertEqual(entries[0]["outcome"], "NARROWS_PRIOR")
        self.assertEqual(
            position["walked_back_followup_id"],
            entries[0]["followup_id"],
        )

    def test_followup_after_walkback_reverts_before_model(self):
        pid = self.open()
        self.runtime.default = {"outcome": "NARROWS_PRIOR"}
        self.contract.submit_followup(pid, NARROWS)
        self.refuse(
            lambda: self.contract.submit_followup(pid, KEEPS),
            "Position has already been walked back",
        )

    def test_walkback_unlocks_one_time_reliance_withdrawal(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "Counterparty")

        self.sender(PRIMARY)
        self.runtime.default = {"outcome": "NARROWS_PRIOR"}
        self.contract.submit_followup(pid, NARROWS)

        self.sender(COUNTERPART)
        self.contract.withdraw_reliance(pid)
        position = self.contract.get_position(pid)
        reliance = self.contract.get_reliance(pid, COUNTERPART)
        self.assertEqual(position["reliance_count"], 1)
        self.assertEqual(position["standing_reliance_count"], 0)
        self.assertFalse(reliance["active"])

        self.refuse(
            lambda: self.contract.withdraw_reliance(pid),
            "Reliance was already withdrawn",
        )

    def test_unregistered_wallet_cannot_withdraw_after_walkback(self):
        pid = self.open()
        self.runtime.default = {"outcome": "NARROWS_PRIOR"}
        self.contract.submit_followup(pid, NARROWS)
        self.sender(OUTSIDER)
        self.refuse(
            lambda: self.contract.withdraw_reliance(pid),
            "Wallet has no registered reliance",
        )

    def test_registration_closes_after_walkback(self):
        pid = self.open()
        self.runtime.default = {"outcome": "NARROWS_PRIOR"}
        self.contract.submit_followup(pid, NARROWS)
        self.sender(COUNTERPART)
        self.refuse(
            lambda: self.contract.register_reliance(pid, "Late"),
            "Position is no longer standing",
        )

    def test_followup_duplicate_key_collapses_internal_whitespace(self):
        pid = self.open()
        first = "This   wording\nkeeps the prior scope."
        second = "This wording keeps the prior scope."
        self.contract.submit_followup(pid, first)
        self.refuse(
            lambda: self.contract.submit_followup(pid, second),
            "Follow-up already exists",
        )
        entry = self.contract.get_followups(pid, 0, 10)[0]
        self.assertEqual(entry["text"], first.strip())

    def test_followup_input_checks_precede_model(self):
        pid = self.open()
        for text, message in (
            ("", "Follow-up text cannot"),
            ("x" * 601, "Follow-up text is too long"),
            (self.module.EARLIER_OPEN, "Reserved prompt token"),
        ):
            with self.subTest(message=message):
                self.refuse(
                    lambda text=text: self.contract.submit_followup(pid, text),
                    message,
                )

    def test_model_call_limit_precedes_text_validation(self):
        pid = self.open()
        self.set_position(
            pid,
            model_calls=self.module.u256(5),
        )
        self.refuse(
            lambda: self.contract.submit_followup(pid, ""),
            "Model call limit reached",
        )

    def test_followup_limit_precedes_model_call_limit(self):
        pid = self.open()
        self.set_position(
            pid,
            followup_count=self.module.u256(20),
            model_calls=self.module.u256(5),
        )
        self.refuse(
            lambda: self.contract.submit_followup(pid, KEEPS),
            "Follow-up limit reached",
        )

    def test_five_accepted_keeps_calls_exhaust_model_budget(self):
        pid = self.open()
        for index in range(5):
            self.contract.submit_followup(
                pid,
                "Scope preserving follow-up number " + str(index),
            )
        self.assertEqual(self.contract.get_position(pid)["model_calls"], 5)
        self.refuse(
            lambda: self.contract.submit_followup(pid, "Sixth wording"),
            "Model call limit reached",
        )

    def test_malformed_outputs_fail_toward_keeps_prior(self):
        variants = (
            "not json",
            {"unexpected": "value"},
            ["NARROWS_PRIOR"],
            RuntimeError("model unavailable"),
        )
        for index, output in enumerate(variants):
            with self.subTest(output=repr(output)):
                module, contract, gl, runtime = load_contract()
                topic = TOPIC + " " + str(index)
                contract.open_position(topic, BASELINE)
                pid = contract._position_id_for(PRIMARY, topic)
                runtime.default = output
                contract.submit_followup(pid, "Later wording " + str(index))
                self.assertEqual(
                    contract.get_position(pid)["state"],
                    "STANDING",
                )
                self.assertEqual(
                    contract.get_followups(pid, 0, 10)[0]["outcome"],
                    "KEEPS_PRIOR",
                )

    def test_json_string_and_fenced_json_are_supported(self):
        for index, output in enumerate((
            json.dumps({"outcome": "KEEPS_PRIOR"}),
            "json\n" + json.dumps({"outcome": "NARROWS_PRIOR"}),
        )):
            with self.subTest(index=index):
                module, contract, gl, runtime = load_contract()
                topic = TOPIC + " parse " + str(index)
                contract.open_position(topic, BASELINE)
                pid = contract._position_id_for(PRIMARY, topic)
                if index == 1:
                    output = (
                        chr(96) * 3
                        + output
                        + "\n"
                        + chr(96) * 3
                    )
                runtime.default = output
                contract.submit_followup(pid, "Later wording " + str(index))
                expected = "STANDING" if index == 0 else "WALKED_BACK"
                self.assertEqual(contract.get_position(pid)["state"], expected)

    def test_leader_validator_divergence_reverts_without_state(self):
        pid = self.open()
        self.runtime.outputs = [
            {"outcome": "KEEPS_PRIOR"},
            {"outcome": "NARROWS_PRIOR"},
        ]
        self.refuse(
            lambda: self.contract.submit_followup(pid, KEEPS),
            "did not converge",
            model_delta=1,
        )

    def test_prompt_contains_only_three_dynamic_inputs(self):
        pid = self.open()
        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "UNIQUE_RELIER_LABEL")
        self.sender(PRIMARY)
        self.contract.submit_followup(pid, "UNIQUE_LATER_TEXT")

        prompt = self.runtime.prompts[0]
        self.assertIn(TOPIC, prompt)
        self.assertIn(BASELINE, prompt)
        self.assertIn("UNIQUE_LATER_TEXT", prompt)
        self.assertNotIn(PRIMARY, prompt)
        self.assertNotIn(COUNTERPART, prompt)
        self.assertNotIn("UNIQUE_RELIER_LABEL", prompt)
        self.assertNotIn("STANDING", prompt)

    def test_followup_and_reliance_views_paginate_history(self):
        pid = self.open()
        self.contract.submit_followup(pid, "First preserving wording")
        self.contract.submit_followup(pid, "Second preserving wording")

        self.sender(COUNTERPART)
        self.contract.register_reliance(pid, "Counterparty")
        self.sender(OUTSIDER)
        self.contract.register_reliance(pid, "Outsider")

        followups = self.contract.get_followups(pid, 1, 1)
        reliances = self.contract.get_reliances(pid, 1, 1)
        self.assertEqual(followups[0]["index"], 2)
        self.assertEqual(reliances[0]["index"], 2)
        self.assertEqual(reliances[0]["wallet"], OUTSIDER)

    def test_invalid_pagination_is_refused(self):
        pid = self.open()
        for call in (
            lambda: self.contract.get_followups(pid, -1, 1),
            lambda: self.contract.get_followups(pid, 0, 0),
            lambda: self.contract.get_reliances(pid, -1, 1),
            lambda: self.contract.get_reliances(pid, 0, 51),
        ):
            with self.subTest(call=call):
                with self.assertRaises(UserError):
                    call()

    def test_views_return_empty_for_unknown_ids(self):
        self.assertEqual(self.contract.get_position("missing"), {})
        self.assertEqual(self.contract.get_followup("missing"), {})

    def test_limits_are_explicit(self):
        limits = self.contract.get_limits()
        self.assertEqual(limits["max_model_calls_per_position"], 5)
        self.assertEqual(limits["max_reliances_per_position"], 50)


if __name__ == "__main__":
    unittest.main()
