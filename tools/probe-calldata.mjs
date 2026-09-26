import { abi } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { encodeFunctionData, isAddress } from 'viem';
import { writeFile } from 'node:fs/promises';

const RPC_URL = process.env.STUDIONET_RPC_URL || 'https://studio.genlayer.com/api';
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const FROM_ADDRESS = process.env.FROM_ADDRESS;
const POSITION_ID = process.env.POSITION_ID;

function required(name, value) {
  if (!value) throw new Error(`${name} is required`);
  return value;
}

required('CONTRACT_ADDRESS', CONTRACT_ADDRESS);
required('FROM_ADDRESS', FROM_ADDRESS);
required('POSITION_ID', POSITION_ID);
if (!isAddress(CONTRACT_ADDRESS)) throw new Error('CONTRACT_ADDRESS is not an EVM address');
if (!isAddress(FROM_ADDRESS)) throw new Error('FROM_ADDRESS is not an EVM address');
if (!/^[0-9a-fA-F]{64}$/.test(POSITION_ID)) {
  throw new Error('POSITION_ID must be the 64-character hex ID returned by open_position');
}

const CASES = [
  ['C1', 'The audit report will appear inside the release notes rather than on a separate page.'],
  ['C2', 'Every release will still ship with its audit report, and we will add a summary page.'],
  ['C3', 'The audit report will be published for every release, including hotfixes.'],
  ['C4', 'We will publish the audit report for every release, and each report will be signed.'],
  ['C5', 'The audit report will be published for every release, and only the signed copy is official.'],
  ['N1', 'From now on the audit report will be published only for major releases.'],
  ['N2', 'We will publish the audit report for every release where a customer requests one.'],
  ['N3', 'Audit reports will be shared with enterprise customers.'],
  ['N4', 'The audit report will be published for every release at our discretion.'],
  ['N5', 'We will summarise audit findings in the changelog.'],
];

const addTransactionAbi = [{
  type: 'function',
  name: 'addTransaction',
  stateMutability: 'nonpayable',
  inputs: [
    { name: '_sender', type: 'address' },
    { name: '_recipient', type: 'address' },
    { name: '_numOfInitialValidators', type: 'uint256' },
    { name: '_maxRotations', type: 'uint256' },
    { name: '_txData', type: 'bytes' },
  ],
  outputs: [],
}];

function makeEnvelope(text) {
  const calldata = abi.calldata.encode(
    abi.calldata.makeCalldataObject('submit_followup', [POSITION_ID, text]),
  );
  const payload = abi.transactions.serialize([calldata, false]);
  const data = encodeFunctionData({
    abi: addTransactionAbi,
    functionName: 'addTransaction',
    args: [FROM_ADDRESS, CONTRACT_ADDRESS, 5n, 3n, payload],
  });
  return { calldata, payload, data };
}

async function rpc(method, params, id) {
  const response = await fetch(RPC_URL, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id, method, params }),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${JSON.stringify(body)}`);
  return body;
}

const results = [];
for (let index = 0; index < CASES.length; index += 1) {
  const [caseId, text] = CASES[index];
  const { calldata, payload, data } = makeEnvelope(text);
  const params = {
    from: FROM_ADDRESS,
    to: studionet.consensusMainContract.address,
    data,
    value: '0x0',
  };
  const row = {
    caseId,
    text,
    calldata,
    calldataBytes: (calldata.length - 2) / 2,
    serializedTransactionBytes: (payload.length - 2) / 2,
    envelopeBytes: (data.length - 2) / 2,
  };
  try {
    row.rpc = await rpc('eth_estimateGas', [params], index + 1);
    row.accepted = !row.rpc.error;
  } catch (error) {
    row.accepted = false;
    row.transportError = error.message;
  }
  results.push(row);
  console.log(`${caseId}: ${row.accepted ? 'ACCEPTED' : 'REJECTED'}`);
}

const artifact = {
  generatedAt: new Date().toISOString(),
  chainId: 61999,
  rpcUrl: RPC_URL,
  contractAddress: CONTRACT_ADDRESS,
  fromAddress: FROM_ADDRESS,
  positionId: POSITION_ID,
  sdk: 'genlayer-js 1.1.8',
  method: 'eth_estimateGas',
  proofBoundary: 'Calldata/envelope acceptance only. This is not proof of consensus execution or a semantic verdict.',
  results,
};
await writeFile(new URL('./calldata-probe-results.json', import.meta.url), `${JSON.stringify(artifact, null, 2)}\n`);

if (results.some((row) => !row.accepted)) process.exitCode = 1;
