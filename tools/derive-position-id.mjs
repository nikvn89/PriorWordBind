import { isAddress, keccak256, toBytes } from 'viem';

const creator = process.env.CREATOR_ADDRESS;
const topic = process.env.TOPIC;

if (!creator || !isAddress(creator)) {
  throw new Error('CREATOR_ADDRESS must be a valid EVM address');
}
if (!topic || topic.trim() !== topic || topic.length === 0) {
  throw new Error('TOPIC must be the exact non-empty, already-trimmed topic submitted on-chain');
}

const payload = `PRIOR_WORD_BIND:POSITION:V1|${creator.toLowerCase()}|${[...topic].length}|${topic}`;
console.log(keccak256(toBytes(payload)).slice(2));
