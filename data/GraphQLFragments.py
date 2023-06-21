
# Fragments

BlockFragment = """  
            fragment BlockFragment on Block {
                id
                timestamp
                txHash
                gasLimit
                gasPrice
                height
                blockHash
                blockSize
                gasPrice
                operatorAccount {
                  ...AccountFragment
                }
              }"""


AccountCreatedAtFragment = """
            fragment AccountCreatedAtFragment on Transaction {
                id
                __typename
                block {
                  id
                  timestamp
                }
            }"""

AccountFragment = """
            fragment AccountFragment on Account {
                id
                address
                __typename
            }"""

UserFragment = """
            fragment UserFragment on User {
                id
                address
                __typename
                createdAtTransaction {
                  ...AccountCreatedAtFragment
                }
                publicKey
              }"""

PoolFragment = """
            fragment PoolFragment on Pool {
                id
                address
                __typename
                createdAtTransaction {
                  ...AccountCreatedAtFragment
                }
                feeBipsAMM
              }"""

TokenFragment_old = """
            fragment TokenFragment on Token {
                id
                name
                symbol
                decimals
                address
              }"""

TokenFragment = """
            fragment TokenFragment on Token {
                id
                symbol
              }"""

NFTFragment = """
          fragment NFTFragment on NonFungibleToken {
            id
            minter {
              ...AccountFragment
            }
            __typename
            nftID
            nftType
            token
          }
        """

AddFragment = """
        fragment AddFragment on Add {
            id
            account {
              ...AccountFragment
            }
            pool {
              ...PoolFragment
            }
            token {
              ...TokenFragment
            }
            feeToken {
              ...TokenFragment
            }
            amount
            fee
            __typename
          }"""

RemoveFragment = """
         fragment RemoveFragment on Remove {
            id
            account {
              ...AccountFragment
            }
            pool {
              ...PoolFragment
            }
            token {
              ...TokenFragment
            }
            feeToken {
              ...TokenFragment
            }
            amount
            fee
            __typename
          }"""

SwapFragment = """
        fragment SwapFragment on Swap {
            id
            account {
              ...AccountFragment
            }
            pool {
              ...PoolFragment
            }
            tokenA {
              ...TokenFragment
            }
            tokenB {
              ...TokenFragment
            }
            pair {
              id
              token0 {
                symbol
              }
              token1 {
                symbol
              }
            }
            tokenAPrice
            tokenBPrice
            fillSA
            fillSB
            fillBA
            fillBB
            protocolFeeA
            protocolFeeB
            feeA
            feeB
            __typename
          }"""

OrderBookTradeFragment = """
          fragment OrderbookTradeFragment on OrderbookTrade {
            id
            accountA {
              ...AccountFragment
            }
            accountB {
              ...AccountFragment
            }
            tokenA {
              ...TokenFragment
            }
            tokenB {
              ...TokenFragment
            }
            pair {
              id
              token0 {
                symbol
              }
              token1 {
                symbol
              }
            }
            tokenAPrice
            tokenBPrice
            fillSA
            fillSB
            fillBA
            fillBB
            fillAmountBorSA
            fillAmountBorSB
            feeA
            feeB
            __typename
          }"""

DepositFragment = """
          fragment DepositFragment on Deposit {
            id
            toAccount {
              ...AccountFragment
            }
            token {
              ...TokenFragment
            }
            amount
            __typename
          }"""

WithdrawalFragment = """
          fragment WithdrawalFragment on Withdrawal {
            id
            fromAccount {
              ...AccountFragment
            }
            token {
              ...TokenFragment
            }
            feeToken {
              ...TokenFragment
            }
            amount
            fee
            __typename
          }"""

TransferFragment = """
         fragment TransferFragment on Transfer {
            id
            fromAccount {
              ...AccountFragment
            }
            toAccount {
              ...AccountFragment
            }
            token {
              ...TokenFragment
            }
            feeToken {
              ...TokenFragment
            }
            amount
            fee
            __typename
          }"""

AccountUpdateFragment = """
          fragment AccountUpdateFragment on AccountUpdate {
            id
            user {
              id
              address
              publicKey
            }
            feeToken {
              ...TokenFragment
            }
            fee
            nonce
            __typename
          }"""

AmmUpdateFragment = """
          fragment AmmUpdateFragment on AmmUpdate {
            id
            pool {
              ...PoolFragment
            }
            tokenID
            feeBips
            tokenWeight
            nonce
            balance
            __typename
          }"""

SignatureVerificationFragment = """
          fragment SignatureVerificationFragment on SignatureVerification {
            id
            account {
              ...AccountFragment
            }
            verificationData
            __typename
          }"""

TradeNFTFragment = """
          fragment TradeNFTFragment on TradeNFT {
            id
            accountSeller {
              ...AccountFragment
            }
            accountBuyer {
              ...AccountFragment
            }
            tradeNFTFragment_Token: token {
              ...TokenFragment
            }
            nfts {
              ...NFTFragment
            }
            realizedNFTPrice
            feeBuyer
            feeSeller
            fillSA
            fillBA
            fillSB
            fillBB
            tokenIDAS
            protocolFeeBuyer
            __typename
          }"""

SwapNFTFragment = """
         fragment SwapNFTFragment on SwapNFT {
            id
            accountA {
              ...AccountFragment
            }
            accountB {
              ...AccountFragment
            }
            nfts {
              ...NFTFragment
            }
            __typename
          }"""

WithdrawalNFTFragment = """
          fragment WithdrawalNFTFragment on WithdrawalNFT {
            id
            fromAccount {
              ...AccountFragment
            }
            fee
            WithdrawalNFTFragment_feeToken: feeToken {
              ...TokenFragment
            }
            nfts {
              ...NFTFragment
            }
            amount
            valid
            __typename
          }"""

TransferNFTFragment = """
          fragment TransferNFTFragment on TransferNFT {
            id
            fromAccount {
              ...AccountFragment
            }
            toAccount {
              ...AccountFragment
            }
            transferNFTFragment_feeToken: feeToken {
              ...TokenFragment
            }
            nfts {
              ...NFTFragment
            }
            fee
            amount
            __typename
          }"""

MintNFTFragment = """
          fragment MintNFTFragment on MintNFT {
            id
            minter {
              ...AccountFragment
            }
            receiver {
              ...AccountFragment
            }
            receiverSlot {
              id
            }
            nft {
              ...NFTFragment
            }
            fee
            mintNFTFragment_feeToken: feeToken {
              ...TokenFragment
            }
            amount
            __typename
          }"""

MintNFTFragmentWithoutNFT = """
          fragment MintNFTFragmentWithoutNFT on MintNFT {
            id
            minter {
              ...AccountFragment
            }
            receiver {
              ...AccountFragment
            }
            receiverSlot {
              id
            }
            fee
            mintNFTFragmentWithoutNFT_feeToken: feeToken {
              ...TokenFragment
            }
            amount
            __typename
          }"""

DataNFTFragment = """
        fragment DataNFTFragment on DataNFT {
            id
            __typename
            accountID
            tokenID
            dataNFTFragment_minter: minter
            tokenAddress
            nftID
            nftType
            data
          }"""
