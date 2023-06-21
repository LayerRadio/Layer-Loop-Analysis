from data.LoopringGraphQLService import *
from data.LoopringApiService import *
from data.constants import SUBGRAPH_API, REST_API, NFTINFOS_API
from model.models import Erc20Tokens, Collection, Account, Nft, TransactionNft
from sqlalchemy import func, and_, or_
import datetime
import re


def erc20_results_2_db(layerapp, db, last_id=-1):
    LRGS = LoopringGraphQLServices(SUBGRAPH_API["LoopringGraph"])
    coroutine = LRGS.GetErc20Tokens(last_id=last_id, to_sql_db=False)
    loop = asyncio.new_event_loop()
    erc20Info = loop.run_until_complete(coroutine)

    tokens = []
    for each_token in erc20Info:
        tokenId = int(each_token['id'])
        internalTokenId = int(each_token['internalID'])
        tokenName = str(each_token['name'])
        symbol = str(each_token['symbol'])
        decimals = int(each_token['decimals'])
        address = str(each_token['address'])

        new_token = Erc20Tokens(tokenId=tokenId,
                                internalTokenId=internalTokenId,
                                tokenName=tokenName,
                                symbol=symbol,
                                decimals=decimals,
                                address=address
                                )
        tokens.append(new_token)

    if len(tokens) == 0:
        pass
    else:
        with layerapp.app_context():
            db.session.add_all(tokens)
            db.session.commit()

def collection_and_nfts_2_db(layerapp, db, collection_address, last_id=-1):
    # check if collection already in the db, if not place it in

    # LRDEBUG # Check if the collection is in the db
    if db.session.query(Collection.collection_address).filter(Collection.collection_address == collection_address).first() is None:
        col_in_db = 0
        max_tx = -1
    else:
        col_in_db = 1
        max_tx = db.session.query(Collection.last_tx).filter(Collection.collection_address == collection_address, Collection.last_tx != 'Slot is empty').order_by(Collection.last_tx.desc()).first()

    LRGS = LoopringGraphQLServices(SUBGRAPH_API["LoopringGraph"])
    coroutine = LRGS.GetCollectionNFTsAll(collectionId=collection_address, include_deposits=1)
    loop = asyncio.new_event_loop()
    try:
        collectionNFTs = loop.run_until_complete(coroutine)
    except Exception as err:
        print('in collection except 1 -> collection_and_nfts_2_db', flush=True)
        raise err

    if not collectionNFTs:
        # then there are no NFTs associalted with the collection
        raise Exception('There are no L2 NFTs associated with this Address 1')

    collection_info = db.session.query(Collection.id, Collection.last_tx).filter(Collection.collection_address == collection_address).first()
    if collection_info is None:  # new collection
        print('says new collection...', flush=True)
        last_tx = str(-1)
        update_collection = Collection(loopring_id=None,
                                    collection_address=collection_address,
                                    collection_name=None,
                                    active=0,
                                    updating='Updating',
                                    last_updated=datetime.datetime.utcnow(),
                                    last_tx=last_tx)
        with layerapp.app_context():
            db.session.add(update_collection)
            db.session.flush()
            db.session.commit()
            update_collection_id = update_collection.id

    else:  #Collection already exists and then update it and record new NFTs
        update_collection_id = collection_info[0]
        last_tx = collection_info[1]
        temp_update_collection = []
        for each_nft in collectionNFTs:
            # update_nftTest = db.session.query(Nft).filter(Nft.full_nft_id == str(each_nft['id']))
            if db.session.query(Nft.full_nft_id).filter(Nft.full_nft_id == str(each_nft['id'])).first() is None:
                temp_update_collection.append(each_nft)

            elif (each_nft['slots']) and (db.session.query(Nft.last_updated_at_tx).filter(Nft.full_nft_id == str(each_nft['id'])).scalar() < str(each_nft['slots'][0]['lastUpdatedAtTransaction']['id'])) :
                update_nft = db.session.query(Nft).filter(Nft.full_nft_id == str(each_nft['id'])).first()
                update_nft.last_updated_at_tx = str(each_nft['slots'][0]['lastUpdatedAtTransaction']['id'])
                db.session.commit()
                pass

        collectionNFTs = temp_update_collection

    if 1==1: #LRDebug
        # Fetch Nfts and add them to collection
        nfts = []
        accounts = []
        unique_accounts = db.session.query(Account.id).order_by(Account.id.asc()).all()
        unique_accounts = [account for account, in unique_accounts]
        for each_nft in collectionNFTs:
            # print(each_nft, flush=True)
            nft_id = str(each_nft['nftID'])
            if each_nft['slots']:
                last_updated_at_tx = str(each_nft['slots'][0]['lastUpdatedAtTransaction']['id'])
                if last_updated_at_tx > last_tx:
                    # last_tx = last_updated_at_tx
                    pass

            else:
                last_updated_at_tx = -1 # the Slot can be empty, but I think this is only a bug with early NFTs (and making that assumtion) 'Slot is empty'

            full_nft_id = str(each_nft['id'])
            collection_id = update_collection_id  # int(each_nft['internalID'])
            collection_address = str(each_nft['token'])  # will remove this
            total_minted = int(each_nft['mintedAtTransaction']['amount'])
            creator_fee_bips = str(each_nft['creatorFeeBips'])
            nft_type = int(each_nft['nftType'])
            minter_id = int(each_nft['minter']['id'])

            if minter_id not in unique_accounts:
                account_id = minter_id
                account_address = str(each_nft['minter']['address'])
                account_type = str(each_nft['minter']['__typename'])

                new_account = Account(
                    id=account_id,
                    address=account_address,
                    account_type=account_type
                )
                accounts.append(new_account)
                unique_accounts += (minter_id,)

            new_nft = Nft(nft_id=nft_id,
                          full_nft_id=full_nft_id,
                          collection_id=collection_id,
                          collection_address=collection_address,
                          loopring_collection_id=None,
                          total_minted=total_minted,
                          creator_fee_bips=creator_fee_bips,
                          nft_type=nft_type,
                          minter_id=minter_id,
                          last_updated_at_tx=last_updated_at_tx
                          )
            nfts.append(new_nft)

        if len(nfts) == 0:
            pass  # no new tokens
        else:
            print('about to write')
            with layerapp.app_context():
                if len(accounts) > 0:
                    db.session.add_all(accounts)
                    db.session.flush()
                db.session.add_all(nfts)
                db.session.flush()
                db.session.commit()

        print('Before coroutine_nft_tx = LRGS.GetTxsFromNftId(nfts_collection)')
        # Get Transactions of all nfts
        nfts_collection = db.session.query(Nft.full_nft_id).filter(and_(Nft.collection_id==update_collection_id, or_(Nft.last_updated_at_tx>last_tx, Nft.last_updated_at_tx == -1) ) ).order_by(Nft.id.asc()).all()
        print(last_tx, flush=True)
        # nfts_collection = db.session.query(Nft.full_nft_id).filter(Nft.collection_id == update_collection_id).order_by(Nft.id.asc()).all()
        coroutine_nft_tx = LRGS.GetTxsFromNftId(nfts_collection, last_tx)
        collection_txs = loop.run_until_complete(coroutine_nft_tx)
        print('finished collection Data')
        if collection_txs is not None:
            collection_txs_2_db(layerapp, db, collection_txs, update_collection_id)

        #Update the collection 'Updating' field to 0
        with layerapp.app_context():
            collection_update = Collection.query.filter_by(id=update_collection_id).first()
            collection_update.updating = 'Complete'
            collection_update.last_updated = datetime.datetime.utcnow()
            testMax = db.session.query(func.max(TransactionNft.tx_id)).first()
            print('testMax: ' + str(testMax), flush=True)
            collection_update.last_tx = db.session.query(func.max(TransactionNft.tx_id)).filter(TransactionNft.collection_id == update_collection_id).scalar()
            # use NftInfos to get the collection info, in the future this should be switched to use either Loppring api or IPFS
            try:
                nft_collection_address = db.session.query(Collection.collection_address).filter(Collection.id == update_collection_id).first()
                collectionNftInfos = asyncio.get_event_loop().run_until_complete(LoopringApiServices.query_url(NFTINFOS_API["NftInfosApi"], nft_collection_address[0]))
                print(collectionNftInfos['name'], flush=True)

                if collectionNftInfos['name'] != None:
                    print('6woooooo' + str(re.sub(r'[^0-9A-Za-z ,.-]+', '', collectionNftInfos['name'])))
                    collection_update.name = str(re.sub(r'[^0-9A-Za-z ,.-]', '', collectionNftInfos['name']))
            except:
                pass
            db.session.commit()

        try:
            nft_collection_address = db.session.query(Collection.collection_address).filter(Collection.id == update_collection_id).first()

        except Exception as err:
            print('in collection except 2', flush=True)
            raise err

    else:
        # this means it has already been in the db, if updating is true, remove and start again, else update
        pass


def collection_txs_2_db(layerapp, db, collection_txs, collection_id, last_id=-1):
    nfts_tx = []
    accounts = []
    unique_accounts = db.session.query(Account.id).order_by(Account.id.asc()).all()
    unique_accounts = [account for account, in unique_accounts]  # put the tuple result to list
    df_tok = pd.read_sql(sql="SELECT id, decimals FROM erc20Tokens", con=db.engine)

    for each_tx in collection_txs:
        tx_id = str(each_tx['id'])
        nft_id = each_tx['nfts'][0]['nftID']
        full_nft_id = each_tx['nfts'][0]['id']
        collection_id = collection_id
        tx_typename = each_tx['__typename']
        block_id = each_tx['block']['id']
        block_timestamp = datetime.datetime.fromtimestamp(int(each_tx['block']['timestamp']), datetime.timezone.utc)

        if each_tx['__typename'] == 'MintNFT':
            amount = each_tx['amount']
            from_acct_id = int(each_tx['minter']['id'])
            to_acct_id = int(each_tx['receiver']['id'])
            from_fee_token_id = int(each_tx['feeToken']['id'])  # updated name to add from
            from_fee = float(each_tx['fee']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == from_fee_token_id].values[0])
            to_fee = None
            to_fee_token_id = None
            realized_nft_price = None
            fill_sa = None
            fill_ba = None
            fill_sb = None
            fill_bb = None
            token_IDAS = None

        elif each_tx['__typename'] == 'TransferNFT':
            amount = each_tx['amount']
            from_acct_id = int(each_tx['fromAcct']['id'])
            to_acct_id = int(each_tx['toAcct']['id'])
            from_fee_token_id = int(each_tx['feeToken']['id'])
            from_fee = float(each_tx['fee']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == from_fee_token_id].values[0])
            to_fee = None
            to_fee_token_id = None
            realized_nft_price = None
            fill_sa = None
            fill_ba = None
            fill_sb = None
            fill_bb = None
            token_IDAS = None

        elif each_tx['__typename'] == 'TradeNFT':
            amount = each_tx['fillBA']
            from_acct_id = int(each_tx['accountSeller']['id'])
            to_acct_id = int(each_tx['accountBuyer']['id'])
            from_fee_token_id = int(each_tx['token']['id'])
            from_fee = float(each_tx['feeSeller']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == from_fee_token_id].values[0])
            to_fee_token_id = int(each_tx['token']['id'])
            to_fee = float(each_tx['feeBuyer']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == to_fee_token_id].values[0])
            fill_sa = each_tx['fillSA']
            fill_ba = each_tx['fillBA']
            fill_sb = each_tx['fillSB']
            fill_bb = each_tx['fillBB']
            token_IDAS = int(each_tx['tokenIDAS'])
            realized_nft_price = float(each_tx['realizedNFTPrice']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == token_IDAS].values[0])

        elif each_tx['__typename'] == 'WithdrawalNFT':
            amount = each_tx['amount']
            from_acct_id = int(each_tx['fromAcct']['id'])
            to_acct_id = None
            from_fee_token_id = int(each_tx['withdrawalFee']['id'])
            from_fee = float(each_tx['fee']) / 10 ** float(df_tok['decimals'].loc[df_tok['id'] == from_fee_token_id].values[0])
            to_fee = None
            to_fee_token_id = None
            realized_nft_price = None
            fill_sa = None
            fill_ba = None
            fill_sb = None
            fill_bb = None
            token_IDAS = None

        elif each_tx['__typename'] == 'SwapNFT':
            # no nfts swaps as of 20230419
            pass
        else:
            print('something else Debug: the typename is: ' + str(each_tx['__typename']))

        if ((from_acct_id not in unique_accounts) and (from_acct_id!=None)):
            account_id = from_acct_id
            if each_tx['__typename'] in ['MintNFT']:
                account_address = str(each_tx['minter']['address'])
                account_type = str(each_tx['minter']['__typename'])

            elif each_tx['__typename'] in ['TransferNFT', 'WithdrawalNFT']:
                account_address = str(each_tx['fromAcct']['address'])
                account_type = str(each_tx['fromAcct']['__typename'])

            elif each_tx['__typename'] in ['TradeNFT']:
                account_address = str(each_tx['accountSeller']['address'])
                account_type = str(each_tx['accountSeller']['__typename'])

            elif each_tx['__typename'] in ['SwapNFT']:
                account_address = str(each_tx['accountA']['address'])
                account_type = str(each_tx['accountA']['__typename'])

            new_account = Account(
                id=account_id,
                address=account_address,
                account_type=account_type
            )
            accounts.append(new_account)
            unique_accounts += [from_acct_id]

        if ((to_acct_id not in unique_accounts) and (to_acct_id!=None)):
            account_id = to_acct_id
            if each_tx['__typename'] in ['MintNFT']:
                account_address = str(each_tx['receiver']['address'])
                account_type = str(each_tx['receiver']['__typename'])

            elif each_tx['__typename'] in ['TransferNFT', 'WithdrawalNFT']:
                account_address = str(each_tx['toAcct']['address'])
                account_type = str(each_tx['toAcct']['__typename'])

            elif each_tx['__typename'] in ['TradeNFT']:
                account_address = str(each_tx['accountBuyer']['address'])
                account_type = str(each_tx['accountBuyer']['__typename'])

            elif each_tx['__typename'] in ['SwapNFT']:
                account_address = str(each_tx['accountB']['address'])
                account_type = str(each_tx['accountB']['__typename'])

            new_account = Account(
                id=account_id,
                address=account_address,
                account_type=account_type
            )
            accounts.append(new_account)
            unique_accounts += [to_acct_id]

        new_nft_tx = TransactionNft(tx_id=tx_id,
                                     nft_id=nft_id,
                                     full_nft_id=full_nft_id,
                                     collection_id=collection_id,
                                     tx_typename=tx_typename,
                                     from_fee=from_fee,
                                     from_fee_token_id=from_fee_token_id,
                                     to_fee=to_fee,
                                     to_fee_token_id=to_fee_token_id,
                                     amount=amount,
                                     block_id=block_id,
                                     block_timestamp=block_timestamp,
                                     from_acct_id=from_acct_id,
                                     to_acct_id=to_acct_id,
                                     realized_nft_price=realized_nft_price,
                                     fill_sa=fill_sa,
                                     fill_ba=fill_ba,
                                     fill_sb=fill_sb,
                                     fill_bb=fill_bb,
                                     token_IDAS=token_IDAS
                                    )
        nfts_tx.append(new_nft_tx)

    with layerapp.app_context():
        if len(accounts) > 0:
            db.session.add_all(accounts)
            db.session.flush()
        db.session.add_all(nfts_tx)
        db.session.flush()
        db.session.commit()

    pass
