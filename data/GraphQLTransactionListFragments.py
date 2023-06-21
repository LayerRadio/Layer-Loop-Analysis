
# Transaction List Fragments

Account = """
            fragment AccountFragment on Account {
                id
                address
                __typename
            }"""

Token_old = """
            fragment TokenFragment on Token {
                id
                name
                symbol
                decimals
              }"""

Token = """
            fragment TokenFragment on Token {
                id
                symbol
                decimals
              }"""

Swap = """
        fragment SwapFragment on Swap {
            id
            account {
              ...AccountFragment
            }
            pool {
              ...AccountFragment
            }
            tokenA {
              ...TokenFragment
            }
            tokenB {
              ...TokenFragment
            }
            fillSA
            fillSB
            fillBA
            fillBB
            feeA
            feeB
            __typename
          }"""

Add = """
        fragment AddFragment on Add {
            id
            account {
              ...AccountFragment
            }
            pool {
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

Remove = """
         fragment RemoveFragment on Remove {
            id
            account {
              ...AccountFragment
            }
            pool {
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

OrderBookTrade = """
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

Deposit = """
          fragment DepositFragment on Deposit {
            id
            toAcct: toAccount {
              ...AccountFragment
            }
            token {
              ...TokenFragment
            }
            amount
            __typename
          }"""

Withdrawal = """
          fragment WithdrawalFragment on Withdrawal {
            id
            fromAcct: fromAccount {
              ...AccountFragment
            }
            WithdrawalToken: token {
              ...TokenFragment
            }
            WithdrawalFeeToken: feeToken {
              ...TokenFragment
            }
            amount
            fee
            __typename
          }"""

Transfer = """
         fragment TransferFragment on Transfer {
            id
            fromAcct: fromAccount {
              ...AccountFragment
            }
            toAcct: toAccount {
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

AccountUpdate = """
          fragment AccountUpdateFragment on AccountUpdate {
            id
            user {
              ...AccountFragment
            }
            feeToken {
              ...TokenFragment
            }
            fee
            __typename
          }"""

AmmUpdate = """
          fragment AmmUpdateFragment on AmmUpdate {
            id
            pool {
              ...AccountFragment
            }
            balance
            __typename
          }"""

SignatureVerification = """
          fragment SignatureVerificationFragment on SignatureVerification {
            id
            account {
              ...AccountFragment
            }
            __typename
          }"""

TradeNFT = """
          fragment TradeNFTFragment on TradeNFT {
            id
            accountSeller {
              ...AccountFragment
            }
            accountBuyer {
              ...AccountFragment
            }
            token {
              ...TokenFragment
            }
            realizedNFTPrice
            feeBuyer
            feeSeller
            fillSA
            fillBA
            fillSB
            fillBB
            tokenIDAS
            __typename
          }"""

SwapNFT = """
         fragment SwapNFTFragment on SwapNFT {
            id
            accountA {
              ...AccountFragment
            }
            accountB {
              ...AccountFragment
            }
            __typename
          }"""

WithdrawalNFT = """
          fragment WithdrawalNFTFragment on WithdrawalNFT {
            id
            fromAcct: fromAccount {
              ...AccountFragment
            }
            fee
            withdrawalFee: feeToken {
              ...TokenFragment
            }
            amount
            __typename
          }"""

TransferNFT = """
          fragment TransferNFTFragment on TransferNFT {
            id
            fromAcct: fromAccount {
              ...AccountFragment
            }
            toAcct: toAccount {
              ...AccountFragment
            }
            feeToken {
              ...TokenFragment
            }
            fee
            amount
            __typename
          }"""

MintNFT = """
          fragment MintNFTFragment on MintNFT {
            id
            minter {
              ...AccountFragment
            }
            receiver {
              ...AccountFragment
            }
            fee
            feeToken {
              ...TokenFragment
            }
            amount
            __typename
          }"""

DataNFT = """
          fragment DataNFTFragment on DataNFT {
            id
            accountID
            __typename
          }"""

AllFragments = Account \
    + Token \
    + Add \
    + Remove \
    + Swap \
    + OrderBookTrade \
    + Deposit \
    + Withdrawal \
    + Transfer \
    + AccountUpdate \
    + AmmUpdate \
    + SignatureVerification \
    + TradeNFT \
    + SwapNFT \
    + WithdrawalNFT \
    + TransferNFT \
    + MintNFT \
    + DataNFT

