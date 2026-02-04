# Circle CCTP API Reference

## Overview

Cross-Chain Transfer Protocol (CCTP) enables native USDC transfers across blockchains without wrapped tokens or liquidity pools.

## Flow

```
Source Chain                    Circle                    Destination Chain
     │                           │                              │
     ├─── depositForBurn ───────>│                              │
     │    (burns USDC)           │                              │
     │                           ├─── attestation ─────────────>│
     │                           │    (signs message)           │
     │                           │                              ├─── receiveMessage
     │                           │                              │    (mints USDC)
```

## Contracts

### TokenMessenger
Handles deposits and burns on the source chain.

**Key Function:**
```solidity
function depositForBurn(
    uint256 amount,
    uint32 destinationDomain,
    bytes32 mintRecipient,
    address burnToken
) external returns (uint64 nonce);
```

### MessageTransmitter
Handles message receiving on the destination chain.

**Key Function:**
```solidity
function receiveMessage(
    bytes calldata message,
    bytes calldata attestation
) external returns (bool success);
```

## Domain IDs

| Chain | Domain ID |
|-------|-----------|
| Ethereum | 0 |
| Avalanche | 1 |
| Optimism | 2 |
| Arbitrum | 3 |
| Noble | 4 |
| Solana | 5 |
| Base | 6 |
| Polygon | 7 |

## Attestation API

### Mainnet
`https://iris-api.circle.com/attestations/{messageHash}`

### Testnet
`https://iris-api-sandbox.circle.com/attestations/{messageHash}`

### Response Format
```json
{
  "attestation": "0x...",
  "message": "0x...",
  "status": "complete"
}
```

Status values: `pending_confirmations`, `pending`, `complete`

## Contract Addresses

### Mainnet

| Chain | TokenMessenger | MessageTransmitter | USDC |
|-------|----------------|-------------------|------|
| Ethereum | 0xBd3fa81B58Ba92a82136038B25aDec7066af3155 | 0x0a992d191DEeC32aFe36203Ad87D7d289a738F81 | 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 |
| Base | 0x1682Ae6375C4E4A97e4B583BC394c861A46D8962 | 0xAD09780d193884d503182aD4588450C416D6F9D4 | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 |
| Polygon | 0x9daF8c91AEFAE50b9c0E69629D3F6Ca40cA3B3FE | 0xF3be9355363857F3e001be68856A2f96b4C39Ba9 | 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359 |
| Arbitrum | 0x19330d10D9Cc8751218eaf51E8885D058642E08A | 0xC30362313FBBA5cf9163F0bb16a0e01f01A896ca | 0xaf88d065e77c8cC2239327C5EDb3A432268e5831 |

### Testnet (Sepolia/Mumbai)

| Chain | TokenMessenger | MessageTransmitter | USDC |
|-------|----------------|-------------------|------|
| Ethereum Sepolia | 0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5 | 0x7865fAfC2db2093669d92c0F33AeEF291086BEFD | 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238 |
| Base Sepolia | 0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5 | 0x7865fAfC2db2093669d92c0F33AeEF291086BEFD | 0x036CbD53842c5426634e7929541eC2318f3dCF7e |
| Arbitrum Sepolia | 0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5 | 0x7865fAfC2db2093669d92c0F33AeEF291086BEFD | 0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d |

## Resources

- [Circle Developer Docs](https://developers.circle.com/cctp)
- [CCTP GitHub](https://github.com/circlefin/evm-cctp-contracts)
- [Bridge Kit SDK](https://developers.circle.com/bridge-kit)
