import time
import asyncio
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError, TransportError
import data.GraphQLFragments as GraphQLFragments
import data.GraphQLTransactionListFragments as GraphQLTransactionListFragments
import pandas as pd
import asyncio


class LoopringGraphQLServices:
    def __init__(self, subgraph):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.transport = AIOHTTPTransport(url=subgraph)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True, execute_timeout=90)
    pass

    async def GetErc20Tokens(self, last_id=-1, to_sql_db=False):  # change name from Erc20Tokens to just Tokens
        params = {
            "skip": 0,
            "first": 1000,  # 1000,
            "where": {"internalID_gt": last_id},
            "orderBy": "internalID",
            "orderDirection": "asc"
        }
        query = gql(
            """
            query erc20Tokens( $where: Token_filter, $first: Int, $skip: Int, $orderDirection: OrderDirection, $orderBy: Token_orderBy) {
                tokens(where: $where, first: $first, skip: $skip, orderBy: $orderBy, orderDirection: $orderDirection) {
                    id
                    internalID
                    name
                    symbol
                    decimals
                    address
                }
            }
            """
        )

        t0 = time.time()
        counter = 0
        results = []
        try:
            while True:
                params["where"] = {"internalID_gt": last_id}
                t1 = time.time()
                temp_result = await self.client.execute_async(query, variable_values=params)
                t2 = time.time()
                results += temp_result['tokens']
                print(t2 - t1)
                if not temp_result['tokens'] or (len(temp_result['tokens']) < params["first"]):
                    print('total length: ' + str(len(results)) + ', temp length' + str())
                    print(len(temp_result['tokens']))
                    break

                last_id = int(temp_result['tokens'][-1]['internalID'])
                await asyncio.sleep(0)
                counter += 1
                print(counter)
        except TransportError as err:
            raise err

        print("end")
        print(counter)
        print(t2 - t0, flush=True)

        return results

    async def GetNFT(self):  # may want to put in params
        params = {
            "id": "0x3f0de067fa6a70eca1f10ebb100e4bb367f1c461-0-0x43778ce982ef806376f9f6b87f426ba9f4e9ee3a-0xffb2a83d13e96ddccd739fba9b6cf22ef3ed5efbf615d547e980d4f37147ed89-3"
        }
        query = gql(
            """
                          query nonFungibleTokenQuery($id: ID!) {
                        nonFungibleToken(id: $id) {
                          id
                          mintedAtTransaction {
                            ...MintNFTFragmentWithoutNFT
                          }
                          ...NFTFragment
                        }
                      }
            """ \
            + GraphQLFragments.AccountFragment \
            + GraphQLFragments.NFTFragment \
            + GraphQLFragments.MintNFTFragmentWithoutNFT \
            + GraphQLFragments.TokenFragment
        )
        try:
            result =  self.client.execute(query, variable_values=params)
        except TransportError as err:
            raise err

        df_data = result['nonFungibleToken']
        df = pd.DataFrame(df_data)
        print(df.columns)
        return await df


    def GetCollectionNFTs(self):  # may want to put in params
        params = {
            "skip": 0,
            "first": 1000,
            "tokenAddress": "0x67f4c51efdef78db04226870654a855274dc4e45",
            "orderBy": "id", # "mintedAt",
            "orderDirection": "desc"
        }

        query = gql(
            """
            query nonFungibleTokens1($where: NonFungibleToken_filter, $skip: Int, $first: Int, $orderDirection: OrderDirection, $orderBy: NonFungibleToken_orderBy) {
                          nonFungibleTokens(where: $where, skip: $skip, first: $first, orderDirection: $orderDirection, orderBy: $orderBy) {
                            ...NFTFragment
                            __typename
                          }
                        }
            """
            + GraphQLFragments.NFTFragment
            + GraphQLFragments.AccountFragment
        )

        try:
            result = self.client.execute(query, variable_values=params)
        except TransportError as err:
            raise err

        df_data = result['nonFungibleTokens']
        df = pd.DataFrame(df_data)
        print(df.columns)
        return df
        # note: may need to add in the where statement that Fudgy has


    async def GetCollectionNFTsAll(self, collectionId, include_deposits = 1):
        params = {
            "skip": 0,
            "first": 1000,
            "lastId": 0,
            "where": { "token_in": [str(collectionId)] , "id_lt": "1",  "minter_": {}},

            "orderBy": "id",
            "orderDirection": "desc"
        }

        if include_deposits==0: # for when an NFT is brought up and then back down, it is minted by the tokens contract (at least for Legacy)
            params["where"]["minter_"] = {"address_not_in": [collectionId]}
        try:
            query = gql(
                """
                query nonFungibleTokens2($where: NonFungibleToken_filter, $skip: Int, $first: Int, $orderDirection: OrderDirection, $orderBy: NonFungibleToken_orderBy) {
                              nonFungibleTokens(where: $where, skip: $skip, first: $first, orderDirection: $orderDirection, orderBy: $orderBy) {
                                ...NFTFragment
                                __typename
                                mintedAtTransaction {
                                  amount
                                }
                                creatorFeeBips
                                slots(orderBy: lastUpdatedAt, orderDirection: desc, first: 1) {
                                    account {
                                        address
                                    }
                                    lastUpdatedAtTransaction {
                                        id
                                    }
                                }
                              }
                            }
                """
                + GraphQLFragments.NFTFragment
                + GraphQLFragments.AccountFragment
            )

            results = []
            try:
                temp_result = await self.client.execute_async(query, variable_values=params)
            except Exception as err:
                print(err, flush=True)
            results += temp_result['nonFungibleTokens']
            counter = 0
            tempSkip = 0
            await asyncio.sleep(0)
            lastId = temp_result['nonFungibleTokens'][-1]['id']

            while True:
                params["where"]["id_lt"] =  lastId
                temp_result = await self.client.execute_async(query, variable_values=params)
                if not temp_result['nonFungibleTokens']:
                    # if the result is empty, then break out of while loop
                    break

                results += temp_result['nonFungibleTokens']
                counter += 1
                print('counter: ' + str(counter), flush=True)
                tempSkip += params["first"]
                lastId = temp_result['nonFungibleTokens'][-1]['id']
                print('lastId: ' + str(lastId), flush=True)
                await asyncio.sleep(0)

        except Exception as err:
            print('index error?', flush=True)
            print(err, flush=True)
            raise err

        return results
        # note: may need to add in the where statement that Fudgy has


    async def GetTxsFromNftId(self, nftIds, last_tx=str(-1)):
        params = {
            "skip": 0,
            "first": 1000,
            "where": {"nfts": ["fullNftId"], "id_gt": last_tx},
            "orderBy": "id",
            "orderDirection": "asc"
        }
        query = gql(
            """
            query nonFungibleTokenQuery3($where: TransactionNFT_filter, $first: Int, $orderDirection: OrderDirection, $orderBy: TransactionNFT_orderBy) {
                transactionNFTs(where: $where, first: $first, orderDirection: $orderDirection, orderBy: $orderBy) {
                    id
                    block {
                        id
                        timestamp
                    }
                    nfts {
                        id
                        nftID
                    }
                    ...TradeNFTFragment
                    ...SwapNFTFragment
                    ...WithdrawalNFTFragment
                    ...TransferNFTFragment
                    ...MintNFTFragment
                }
            }
            """
            + GraphQLTransactionListFragments.Account
            + GraphQLTransactionListFragments.Token
            + GraphQLTransactionListFragments.TradeNFT
            + GraphQLTransactionListFragments.SwapNFT
            + GraphQLTransactionListFragments.WithdrawalNFT
            + GraphQLTransactionListFragments.TransferNFT
            + GraphQLTransactionListFragments.MintNFT
        )

        results = []
        print('length nfts:' + str(len(nftIds)), flush=True)
        print('last txxxxxxxxxxxxxxxxxxxxx:' + str(len(last_tx)), flush=True)
        try:
            await asyncio.sleep(0)
            for i in range(len(nftIds)):
                params['where']['nfts'] = [nftIds[i][0]]  # [nftIds.iat[i]]    # nftIds[i+1]
                temp_result = await self.client.execute_async(query, variable_values=params, serialize_variables=True)
                results += temp_result['transactionNFTs']
                while len(temp_result['transactionNFTs']) == params['first']:  # to account for more than 1000 or 5000 transactions
                    params['where']['id_gt'] = temp_result['transactionNFTs'][-1]['id']  # get last value  # nftIds[i+1]
                    temp_result = await self.client.execute_async(query, variable_values=params)
                    await asyncio.sleep(0)
                    if not temp_result['transactionNFTs']:
                        break
                    results += temp_result['transactionNFTs']
                params['where']['id_gt'] = last_tx
                await asyncio.sleep(0)

        except TransportError as err:
            raise err

        return results


    # This is for Wallet Dashboard, but still in testing.
    # It will not work directly as it is, as code is from when was first written as a Tkinter app
    # Leaving code in for now
    async def GetTxsForUser(self, userID): #async
        params = {
            "skip": 0,
            "first": 1000,
            "userID": userID,
            "whereTx": {"internalID_gt": "0"},
            "orderBy": "internalID",
            "orderDirection": "asc"
        }
        query = gql(
            """
            query nonFungibleTokenQuery4($userID: ID!, $whereTx: Transaction_filter, $first: Int, $skip: Int, $orderDirection: OrderDirection, $orderBy: Transaction_orderBy) {
                account(id: $userID) {
                    transactions(where: $whereTx, orderBy: $orderBy, orderDirection: $orderDirection, first: $first, skip: $skip) {
                        id
                        internalID
                        __typename
                        block {
                            id
                            timestamp
                        }
                        ...AddFragment
                        ...RemoveFragment
                        ...SwapFragment
                        ...OrderbookTradeFragment
                        ...DepositFragment
                        ...WithdrawalFragment
                        ...TransferFragment
                        ...AccountUpdateFragment
                        ...AmmUpdateFragment
                        ...SignatureVerificationFragment
                        ...TradeNFTFragment
                        ...SwapNFTFragment
                        ...WithdrawalNFTFragment
                        ...TransferNFTFragment
                        ...MintNFTFragment
                        ...DataNFTFragment
                    
                    }
                }
            }
            """
            + GraphQLTransactionListFragments.AllFragments
        )

        try:
            df = dc.GetAllTxForCollection()  # no longer using dc, but will address in future when I start working on Wallets again
            t0 = time.time()
            result = await self.client.execute_async(query, variable_values=params)
            t1 = time.time()
            print(t1-t0)
            await asyncio.sleep(0)
            df_data = result['account']['transactions']
            df.results_to_dataframe(df_data, userID)
            counter = 0
            tempSkip = 0
            lastId = df.main_dataframe["internalID"].iloc[-1]
            while True:
                params["whereTx"]["internalID_gt"] = lastId
                t1 = time.time()
                result = await self.client.execute_async(query, variable_values=params)
                t2 = time.time()
                print(t2 - t1)
                if not result['account']['transactions']:  # || :
                    print(df.main_dataframe.shape)
                    break
                df_data = result['account']['transactions']
                df.results_to_dataframe(df_data, userID)
                counter += 1
                print(counter)
                tempSkip += params["first"]
                lastId = df.main_dataframe["internalID"].iloc[-1]

                await asyncio.sleep(0)
        except TransportError as err:
            print('unhappy chicken 1')
            print(err, flush=True)
            raise err

        print(counter)
        print(t2 - t0)
        df.assure_typing()
        df.convert_to_decimal()
        return df


