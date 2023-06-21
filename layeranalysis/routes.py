
from flask import Flask, render_template, request, redirect, flash
from sqlalchemy.sql import func, case, desc, null, asc, union_all, cast, and_, literal_column
from sqlalchemy.orm import aliased
from layeranalysis import layerapp, db
from layeranalysis.charts_plotly.charts import getNftSales, getNftNetwork
from layeranalysis.forms import CollectionAddressForm  # CollectionForm,WelcomeUserForm,DropDownCheckBox,
from model.models import Erc20Tokens, Account, Collection, TransactionNft, Nft
from data.LoopringGraphQL2Db import erc20_results_2_db, collection_and_nfts_2_db
import pandas as pd
from data.constants import BURN_IDS
import plotly
import plotly.express as px
import json
from sqlalchemy import Float, Integer
import datetime
import os


layerapp.secret_key = os.urandom(24)  # "ANny-string-1234587u78"


@layerapp.before_first_request
def setup():
    last_token_id = db.session.query(Erc20Tokens.id, Erc20Tokens.name).order_by(Erc20Tokens.id.desc()).first()
    print('LRDEBUG setup', flush=True)
    try:
        if last_token_id is None:
            erc20_results_2_db(layerapp, db)
        else:
            print(last_token_id[0], flush=True)
            erc20_results_2_db(layerapp, db, last_token_id[0])
    except Exception as err:
        print('Error in setup', flush=True)
        print(err, flush=True)

@layerapp.route('/')
@layerapp.route('/home')
def home():
    return render_template("home.html")


@layerapp.route('/about')
def about():
    return render_template("about.html")


@layerapp.route('/collection', methods=["GET","POST"])
def collection():
    form = CollectionAddressForm()
    if form.validate_on_submit():
        print('wiiiiiiiiiiiii', flush=True)
        # return f'''<h4>Hello {form.name.data}</h4>'''
        # print({form1.name.data})
        #return render_template("collection.html", form=form1)
        pass

    if request.method == 'POST':
        # print('waaaaaaaaaaaaa', flush=True)
        # print(request.form.getlist('mycheckbox'), flush=True)
        # print(request.form.getlist('mycheckbox2'), flush=True)
        # print(request.form.getlist('SearchBar2'), flush=True)
        # print(str(form.address.data) + ' in if statement')
        try:
            collection_and_nfts_2_db(layerapp, db, str(form.address.data).lower())
            flash('Successfully Fetched the collection: ' + str(form.address.data).lower(), 'categoryFetchSuccess')
        except Exception as err:
            print('Error fetching collection: ' + str(form.address.data).lower() + ', with Error: ' + str(err), flush=True)
            flash('Error fetching collection ' + str(form.address.data).lower() + ': ' + str(err), 'categoryFetchError')

        print('ran the collection address', flush=True)

    collection_table = db.session.query(Collection.id, Collection.collection_address, Collection.name, Collection.active,
                                        Collection.updating, Collection.last_updated).order_by(Collection.last_updated.desc())

    return render_template("collection.html", form=form, contacts=collection_table)


@layerapp.route('/updateCollection', methods=["GET","POST"])
def updateCollection():
    print('in the updateCollection!')
    if request.method == 'POST':
        try:
            with layerapp.app_context():
                db.session.query(Collection).filter(Collection.active == 1).update({Collection.active: 0}, synchronize_session=False)
                db.session.commit()

            for getid in request.form.getlist('mycheckbox1'):
                if request.form['submit_button']=='Load All Selected items in Dashboard':
                    with layerapp.app_context():
                        activate_collection = db.session.query(Collection).filter(Collection.id==getid).first()
                        activate_collection.active = 1
                        db.session.commit()
                    flash('Checked Collections succesfully loaded and can be viewed in the Dashboard', 'flashUpdateMessageSuccess')
                elif request.form['submit_button'] == 'Update All Selected items':
                    update_collection = db.session.query(Collection.collection_address).filter(Collection.id == getid).all()
                    for each_coll in update_collection:
                        print(str(each_coll[0]), flush=True)
                        collection_and_nfts_2_db(layerapp, db, str(each_coll[0]))
                    flash('Checked Collections successfully updated: ' + str(each_coll[0]), 'flashUpdateMessageSuccess')
                elif request.form['submit_button'] == 'Delete All Selected items':
                    print(getid)
                    with layerapp.app_context():
                        delete_collection = db.session.query(Collection).filter(Collection.id==getid).first()
                        db.session.delete(delete_collection)
                        db.session.commit()
                    flash('Successfully deleted Collections', 'flashUpdateMessageSuccess')

                else:
                    flash('Please check the box(s) for the Action to take place', 'flashUpdateMessageSuccess')

        except Exception as err:
            flash('Error: ' + str(err), 'flashUpdateMessageError')

    return redirect('/collection')


@layerapp.route('/collection_dashboard')
def collection_dashboard():
    active_collections = db.session.query(Collection.id).filter(Collection.active == 1)
    active_collections_address = db.session.query(Collection.collection_address).filter(Collection.active == 1)
    active_collections_account_id = db.session.query(Account.id).filter(Account.address.in_(active_collections_address))
    # TODO: cleanup query overall_info
    overall_info = db.session.query(func.count(TransactionNft.tx_typename).label('Total_Tx')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'MintNFT', cast(1, Integer))
                                                , else_=cast(0, Integer))).label('Tx_Mint')
                                    , func.sum(case((TransactionNft.tx_typename == 'MintNFT', cast(TransactionNft.amount, Integer)), else_=cast(0, Integer))).label('Total_Minted')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TransferNFT', TransactionNft.to_acct_id.in_(BURN_IDS)), cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Burned')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'WithdrawalNFT',
                                              cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Withdrawal')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'MintNFT', TransactionNft.from_acct_id.in_(active_collections_account_id)),
                                              cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Deposited')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'TransferNFT',
                                              cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Transfer')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TransferNFT', TransactionNft.to_acct_id.notin_(BURN_IDS)),
                                              cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Transfer_NotBurned')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'TransferNFT',
                                              cast(1, Integer))
                                             , else_=cast(0, Integer))).label('Total_Tx_Transfer')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TransferNFT', TransactionNft.to_acct_id.notin_(BURN_IDS)),
                                              cast(1, Integer))
                                             , else_=cast(0, Integer))).label('Total_Tx_Transfer_NotBurned')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'TradeNFT',
                                              cast(TransactionNft.amount, Integer))
                                             , else_=cast(0, Integer))).label('Total_Traded')
                                    , func.sum(
                                        case((TransactionNft.tx_typename == 'TradeNFT',
                                              cast(1, Integer))
                                             , else_=cast(0, Integer))).label('Total_Tx_Traded')
                                    #Sales
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TradeNFT', TransactionNft.token_IDAS == 1),
                                              cast(TransactionNft.realized_nft_price, Float))
                                             , else_=cast(0.0, Float))).label('Sales_LRC')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TradeNFT', TransactionNft.token_IDAS == 0),
                                              cast(TransactionNft.realized_nft_price, Float))
                                             , else_=cast(0.0, Float))).label('Sales_ETH')
                                    # Royalties
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TradeNFT', TransactionNft.token_IDAS == 1),
                                              cast(TransactionNft.realized_nft_price, Float) * cast(Nft.creator_fee_bips, Float) * cast(0.01, Float))
                                             , else_=cast(0.0, Float))).label('Royalties_LRC')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'TradeNFT', TransactionNft.token_IDAS == 0),
                                              cast(TransactionNft.realized_nft_price, Float) * cast(Nft.creator_fee_bips, Float) * cast(0.01, Float))
                                             , else_=cast(0.0, Float))).label('Royalties_ETH')
                                    # Fees
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename != 'MintNFT', TransactionNft.from_fee_token_id == 1),
                                              cast(TransactionNft.from_fee, Float))
                                             , else_=cast(0.0, Float))).label('from_fee_sales_LRC')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename != 'MintNFT', TransactionNft.from_fee_token_id == 0),
                                              cast(TransactionNft.from_fee, Float))
                                             , else_=cast(0.0, Float))).label('from_fee_sales_ETH')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename != 'MintNFT', TransactionNft.to_fee_token_id == 1),
                                              cast(TransactionNft.to_fee, Float))
                                             , else_=cast(0.0, Float))).label('to_fee_sales_LRC')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename != 'MintNFT', TransactionNft.to_fee_token_id == 0),
                                              cast(TransactionNft.to_fee, Float))
                                             , else_=cast(0.0, Float))).label('to_fee_sales_ETH')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'MintNFT', TransactionNft.from_fee_token_id == 1),
                                              cast(TransactionNft.from_fee, Float))
                                             , else_=cast(0.0, Float))).label('mint_fee_LRC')
                                    , func.sum(
                                        case((and_(TransactionNft.tx_typename == 'MintNFT', TransactionNft.from_fee_token_id == 0),
                                              cast(TransactionNft.from_fee, Float))
                                             , else_=cast(0.0, Float))).label('mint_fee_ETH')

                                    , func.count(TransactionNft.tx_typename).label('Count1')
                                    , func.sum(TransactionNft.to_acct_id).label('Sum1')
                                    ) \
                             .join(Nft, TransactionNft.full_nft_id == Nft.full_nft_id) \
                             .filter(TransactionNft.collection_id.in_(active_collections)) \
                             .first()

    return render_template("collection_dashboard.html", overall_info=overall_info) #, total_acct_volume=collection_volume_user, total_acct_sales=collection_sales_from, total_acct_buys=collection_buys_from )


@layerapp.route('/collection_raw')
def collection_raw():
    return render_template("collection_raw.html") #, total_acct_volume=collection_volume_user, total_acct_sales=collection_sales_from, total_acct_buys=collection_buys_from )


@layerapp.route('/callback/table/<endpoint>', methods=["GET","POST"])     #####/<endpoint>')
def cbTable(endpoint):
    active_collections = db.session.query(Collection.id).filter(Collection.active == 1)  # .all()
    if (endpoint == "getSalesByAccount") or (endpoint == "getVolumeByAccount"):
        collection_sales_from = db.session.query(Account.address.label("Account_Address"),
                                                 TransactionNft.from_acct_id.label("Account_ID"),
                                                 func.count(TransactionNft.from_acct_id).label("Total_Sold"),
                                                 case((TransactionNft.token_IDAS == 1, func.sum(TransactionNft.realized_nft_price))).label("Total_Volume_LRC"),
                                                 case((TransactionNft.token_IDAS == 0, func.sum(TransactionNft.realized_nft_price))).label("Total_Volume_ETH"),
                                                 func.sum(TransactionNft.realized_nft_price).label("Total_Price"),
                                                 # TransactionNft.token_IDAS,
                                                 func.sum(TransactionNft.from_fee).label("Total_From_Fee"),
                                                 func.sum(TransactionNft.to_fee).label("Total_To_Fee")
                                                 ) \
                                            .join(Account, TransactionNft.from_acct_id == Account.id) \
                                            .filter(TransactionNft.collection_id.in_(active_collections), TransactionNft.tx_typename=='TradeNFT') \
                                            .group_by(TransactionNft.tx_typename, TransactionNft.from_acct_id, Account.address, TransactionNft.token_IDAS)

        if endpoint == "getSalesByAccount":
            results_to_dict = {'data': [dict(data._mapping) for data in collection_sales_from]}

    if (endpoint == "getBuysByAccount") or (endpoint == "getVolumeByAccount"):
        collection_buys_from = db.session.query(Account.address.label("Account_Address"),
                                                 TransactionNft.to_acct_id.label("Account_ID"),
                                                 func.count(TransactionNft.to_acct_id).label("Total_Sold"),
                                                 case((TransactionNft.token_IDAS == 1, func.sum(TransactionNft.realized_nft_price))).label("Total_Volume_LRC"),
                                                 case((TransactionNft.token_IDAS == 0, func.sum(TransactionNft.realized_nft_price))).label("Total_Volume_ETH"),
                                                 func.sum(TransactionNft.realized_nft_price).label("Total_Price"),
                                                 # TransactionNft.token_IDAS,
                                                 func.sum(TransactionNft.from_fee).label("Total_From_Fee"),
                                                 func.sum(TransactionNft.to_fee).label("Total_To_Fee")
                                                 ) \
                                            .join(Account, TransactionNft.to_acct_id==Account.id) \
                                            .filter( TransactionNft.collection_id.in_(active_collections), TransactionNft.tx_typename=='TradeNFT') \
                                            .group_by(TransactionNft.tx_typename, TransactionNft.to_acct_id, Account.address, TransactionNft.token_IDAS)

        if endpoint == "getBuysByAccount":
            results_to_dict = {'data': [dict(data._mapping) for data in collection_buys_from]}

    if endpoint == "getVolumeByAccount":
        q = collection_sales_from.union_all(collection_buys_from).subquery('subquery_name')
        collection_volume_user = db.session.query(q.c.Account_Address.label("Account_Address"),
                                                  q.c.Account_ID.label("Account_ID"),
                                                  func.sum(q.c.Total_Sold).label("Total_Sold"),
                                                  func.sum(q.c.Total_Volume_LRC).label("Total_Volume_LRC"),
                                                  func.sum(q.c.Total_Volume_ETH).label("Total_Volume_ETH"),
                                                  func.sum(q.c.Total_Price).label("Total_Price"),
                                                  # func.sum(q.c.token_IDAS),
                                                  func.sum(q.c.Total_From_Fee).label("Total_From_Fee"),
                                                  func.sum(q.c.Total_To_Fee).label("Total_To_Fee")
                                                  ) \
                                                 .group_by(q.c.Account_ID) \
                                                 .order_by(desc("Total_Volume_LRC"))  #  asc("Account_ID"))  #, desc('Total_Volume_ETH'))  #

        results_to_dict = {'data': [dict(data._mapping) for data in collection_volume_user]}

    if endpoint == "getHoldersByAccount":
        active_collection_addresses = db.session.query(Collection.collection_address).filter(Collection.active == 1)
        active_collection_address_ids = db.session.query(func.coalesce(Account.id, cast(-1, Integer))).filter(Account.address.in_(active_collection_addresses))

        nft_from_account = db.session.query(TransactionNft.nft_id.label("Nft_ID"),
                                            TransactionNft.from_acct_id.label("Account_ID"),
                                            func.sum(cast(TransactionNft.amount, Float) * cast(-1.0, Float)).label("totalFromAmount"),
                                            func.sum(case((TransactionNft.tx_typename == 'WithdrawalNFT', cast(0.0, Float)),
                                                          else_=cast(TransactionNft.amount, Float) * cast(-1.0, Float))).label("TotalWithouWithdrawl"),
                                            func.sum(case((TransactionNft.tx_typename == 'WithdrawalNFT', TransactionNft.amount),
                                                          else_=0.0)).label("Withdrawn"),
                                            null().label('Deposited')) \
                                            .filter(TransactionNft.collection_id.in_(active_collections),TransactionNft.tx_typename!='MintNFT') \
                                            .group_by(TransactionNft.tx_typename, TransactionNft.from_acct_id, TransactionNft.nft_id) #\
        nft_to_account = db.session.query(TransactionNft.nft_id.label("Nft_ID"),
                                          TransactionNft.to_acct_id.label("Account_ID"),
                                          func.sum(cast(TransactionNft.amount, Float)).label("totalFromAmount"),
                                          func.sum(cast(TransactionNft.amount, Float)).label("TotalWithouWithdrawl"),
                                          cast(0,Integer).label("Withdrawn"),
                                          func.sum(case((TransactionNft.tx_typename == 'MintNFT', case((TransactionNft.from_acct_id.in_(active_collection_address_ids), TransactionNft.amount), else_=0.0)),
                                                        else_=0.0)).label('Deposited')) \
                                          .filter(TransactionNft.collection_id.in_(active_collections)) \
                                          .group_by(TransactionNft.tx_typename, TransactionNft.to_acct_id, TransactionNft.nft_id)
        q2 = nft_from_account.union_all(nft_to_account).subquery()

        collection_holders_account = db.session.query(Account.address.label("Account_Address"),
                                                      q2.c.Account_ID.label("Account_ID2"),
                                                      func.sum(cast(q2.c.totalFromAmount, Float)).label("Total_Amount"),
                                                      func.sum(q2.c.TotalWithouWithdrawl).label("TotalWithouWithdrawl"),
                                                      func.sum(q2.c.Withdrawn).label("Withdrawn"),
                                                      func.sum(q2.c.Deposited).label("Deposited")
                                                      ) \
                                                      .join(Account, q2.c.Account_ID.label("Account_ID2") == Account.id) \
                                                      .group_by("Account_ID2", "Account_Address") \
                                                      .order_by(desc("Total_Amount"))

        results_to_dict = {'data': [dict(data._mapping) for data in collection_holders_account]}
        pass

    if endpoint == "getRawCollectionData":
        active_collection_addresses = db.session.query(Collection.collection_address).filter(Collection.active == 1)
        active_collection_address_ids = db.session.query(func.coalesce(Account.id, cast(-1, Integer))).filter(Account.address.in_(active_collection_addresses))

        nft_from_account = db.session.query(
            TransactionNft.nft_id.label("Nft_ID"),
            TransactionNft.from_acct_id.label("Account_ID"),
            func.sum(cast(TransactionNft.amount, Float) * cast(-1.0, Float)).label("totalFromAmount"),
            func.sum(case((TransactionNft.tx_typename == 'WithdrawalNFT',cast(0.0, Float)),else_=cast(TransactionNft.amount, Float) * cast(-1.0, Float))).label("TotalWithouWithdrawl"),
            func.sum(case((TransactionNft.tx_typename == 'WithdrawalNFT',
                           TransactionNft.amount),
                          else_=0.0)).label("Withdrawn"),
            null().label('Deposited')) \
            .filter(TransactionNft.collection_id.in_(active_collections), TransactionNft.tx_typename != 'MintNFT') \
            .group_by(TransactionNft.tx_typename, TransactionNft.from_acct_id, TransactionNft.nft_id)

        nft_to_account = db.session.query(
            TransactionNft.nft_id.label("Nft_ID"),
            TransactionNft.to_acct_id.label("Account_ID"),
            func.sum(cast(TransactionNft.amount, Float)).label("totalFromAmount"),
            func.sum(cast(TransactionNft.amount, Float)).label("TotalWithouWithdrawl"),
            cast(0, Integer).label("Withdrawn"),
            func.sum(case((TransactionNft.tx_typename == 'MintNFT',
                           case((TransactionNft.from_acct_id.in_(active_collection_address_ids),
                                 TransactionNft.amount), else_=0.0))
                          , else_=0.0)).label('Deposited')) \
            .filter(TransactionNft.collection_id.in_(active_collections)) \
            .group_by(TransactionNft.tx_typename, TransactionNft.to_acct_id, TransactionNft.nft_id)

        q2 = nft_from_account.union_all(nft_to_account).subquery()  # 'subquery_name2'
        print("getRawCollectionData 222222222222222222222222222222222222", flush=True)
        collection_holders_account = db.session.query(Account.address.label("Account_Address"),
                                                      q2.c.Account_ID.label("Account_ID3"),
                                                      # q.c.Nft_ID.label("Nft_ID"),
                                                      # func.sum(q2.c.Total_From_tx).label("Total_Num_Tx"),
                                                      func.sum(cast(q2.c.totalFromAmount, Float)).label(
                                                          "Total_Amount"),
                                                      func.sum(q2.c.TotalWithouWithdrawl).label(
                                                          "TotalWithouWithdrawl"),
                                                      func.sum(q2.c.Withdrawn).label("Withdrawn"),
                                                      func.sum(q2.c.Deposited).label("Deposited")
                                                      ) \
            .join(Account, q2.c.Account_ID.label("Account_ID3") == Account.id) \
            .group_by("Account_ID3", "Account_Address") \
            .order_by(desc("Total_Amount"))

        # TODO: Remove old query above
        # New query
        from_fee_sym = aliased(Erc20Tokens)
        to_fee_sym = aliased(Erc20Tokens)
        sell_sym = aliased(Erc20Tokens)
        from_acct = aliased(Account)
        to_acct = aliased(Account)
        cm_id = aliased(Account)
        print("getRawCollectionData 222222222222222222222222222222222222", flush=True)
        # ToDo: Case is a bit slow, considering putting the minter Address should be in the table NFT, so will come back later
        collection_raw_data = db.session.query(TransactionNft.tx_id.label("Tx_Id"),
                                               TransactionNft.nft_id.label("Nft_Id"),
                                               TransactionNft.full_nft_id.label("Full_Nft_Id"),
                                               func.substr(TransactionNft.full_nft_id, 0, 43).label("Minter"),
                                               case((and_(TransactionNft.tx_typename == 'MintNFT',
                                                          cm_id.id.isnot(None))
                                                     , literal_column("'MintNFT (Deposit)'"))
                                                    , else_=TransactionNft.tx_typename).label("Tx_Type"),
                                               TransactionNft.collection_id.label("Coll_Id"),
                                               Collection.collection_address.label("Coll_Addr"),
                                               TransactionNft.from_acct_id.label("From_Acct_Id"),
                                               from_acct.address.label("From_Acct_Addr"),
                                               TransactionNft.to_acct_id.label("To_Acct_Id"),
                                               to_acct.address.label("To_Acct_Address"),
                                               TransactionNft.realized_nft_price.label("Realized_Nft_Price"),
                                               sell_sym.symbol.label("Sell_Sym"),
                                               TransactionNft.from_fee.label("From_Fee"),
                                               from_fee_sym.symbol.label("From_Fee_Sym"),
                                               TransactionNft.to_fee.label("To_Fee"),
                                               to_fee_sym.symbol.label("To_Fee_Sym"),
                                               TransactionNft.amount.label("Amount"),
                                               TransactionNft.block_timestamp.label("Block_Timestamp"),
                                               (cast(TransactionNft.realized_nft_price, Float) * cast(Nft.creator_fee_bips, Float) * 0.01).label("Royalties"),
                                               sell_sym.symbol.label("Royalties_Sym"),
                                               Nft.creator_fee_bips.label("Creator_Fee_Bips")
                                               ) \
            .join(Collection, Collection.id == TransactionNft.collection_id) \
            .join(from_fee_sym, from_fee_sym.id == TransactionNft.from_fee_token_id, isouter=True) \
            .join(to_fee_sym, to_fee_sym.id == TransactionNft.to_fee_token_id, isouter=True) \
            .join(sell_sym, sell_sym.id == TransactionNft.token_IDAS, isouter=True) \
            .join(from_acct, from_acct.id == TransactionNft.from_acct_id, isouter=True) \
            .join(to_acct, to_acct.id == TransactionNft.to_acct_id, isouter=True) \
            .join(Nft, Nft.full_nft_id == TransactionNft.full_nft_id) \
            .join(cm_id, and_(cm_id.id == Nft.minter_id, cm_id.address == Collection.collection_address), isouter=True) \
            .filter(TransactionNft.collection_id.in_(active_collections))

        results_to_dict = {'data': [dict(data._mapping) for data in collection_raw_data]}
        pass

    print('---------------------------------------------------------', flush=True)
    print(request.args.get('data'), flush=True)
    print('---------------------------------------------------------', flush=True)

    return results_to_dict  # {'data': [user.to_dict() for user in User.query]}


@layerapp.route('/callback/chart/<endpoint>', methods=["GET","POST"])
def cbChart(endpoint):
    print('cb(endpoint): 090909090909090909090', flush=True)
    print(request.args.get('data'), flush=True)
    print('cb(endpoint): 090909090909090909090', flush=True)

    if endpoint == "getNftSales":
        return getNftSales(request.args.get('data'))

    if endpoint == "getNftNetwork":
        return getNftNetwork(request.args.get('data'))

    # Todo: add in Error pages such as 400 and 404
    # else:
    #     return "Bad Endpoint", 400


@layerapp.route('/wallet')
def wallet():
    return render_template("wallet.html")


@layerapp.route('/wallet_dashboard')
def wallet_dashboard():
    return render_template("wallet_dashboard.html")
