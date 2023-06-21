from layeranalysis import db


class Erc20Tokens(db.Model):

    __tablename__ = "erc20tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False, nullable=False)
    internal_id = db.Column(db.Integer)
    name = db.Column(db.String)
    symbol = db.Column(db.String)
    decimals = db.Column(db.Integer)
    address = db.Column(db.String)

    def __init__(self, tokenId, internalTokenId, tokenName, symbol, decimals, address):  # tokenId,
        self.id = tokenId
        self.internal_id = internalTokenId
        self.name = tokenName
        self.symbol = symbol
        self.decimals = decimals
        self.address = address


class Collection(db.Model):

    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)  # , autoincrement=False)
    loopring_id = db.Column(db.Integer, nullable=True)
    collection_address = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=True)
    active = db.Column(db.Integer, nullable=False)
    updating = db.Column(db.String, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)
    last_tx = db.Column(db.String, nullable=True)
    nfts = db.relationship('Nft', backref='collection', cascade='all, delete, delete-orphan')
    tx_nfts = db.relationship('TransactionNft', backref='collection', cascade='all, delete, delete-orphan')

    def __init__(self, loopring_id, collection_address, collection_name, active, updating, last_updated, last_tx):
        self.loopring_id = loopring_id
        self.collection_address = collection_address
        self.name = collection_name
        self.active = active
        self.updating = updating
        self.last_updated = last_updated
        self.last_tx = last_tx


class Nft(db.Model):

    __tablename__ = "nft"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nft_id = db.Column(db.String)
    full_nft_id = db.Column(db.String)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE'), nullable=False)
    collection_address = db.Column(db.String)
    loopring_collection_id = db.Column(db.String)
    total_minted = db.Column(db.Integer)
    creator_fee_bips = db.Column(db.String)
    nft_type = db.Column(db.Integer)
    minter_id = db.Column(db.String)
    last_updated_at_tx = db.Column(db.String)
    # nft_txs = db.relationship('TransactionNft', backref='nft', cascade='all, delete, delete-orphan')

    def __init__(self, nft_id, full_nft_id, collection_id, collection_address, loopring_collection_id, total_minted, creator_fee_bips, nft_type, minter_id, last_updated_at_tx):

        self.nft_id = nft_id
        self.full_nft_id = full_nft_id
        self.collection_id = collection_id
        self.collection_address = collection_address
        self.loopring_collection_id = loopring_collection_id
        self.total_minted = total_minted
        self.creator_fee_bips = creator_fee_bips
        self.nft_type = nft_type
        self.minter_id = minter_id
        self.last_updated_at_tx = last_updated_at_tx


class TransactionNft(db.Model):

    __tablename__ = "transaction_nft"

    tx_id = db.Column(db.String, primary_key=True, autoincrement=False)  # Tx id This should be the real primary key (or the Loopring internal tx id)
    # nft_internal = db.Column(db.Integer, db.ForeignKey('nft.id', ondelete='CASCADE'), nullable=False)  # probably should make this a nft int (internal)
    nft_id = db.Column(db.String)
    full_nft_id = db.Column(db.String)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id', ondelete='CASCADE'), nullable=False)  #
    tx_typename = db.Column(db.String)
    from_fee = db.Column(db.Double)
    from_fee_token_id = db.Column(db.Integer)
    to_fee = db.Column(db.Float)
    to_fee_token_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    block_id = db.Column(db.Integer)
    block_timestamp = db.Column(db.DateTime)
    from_acct_id = db.Column(db.Integer)
    to_acct_id = db.Column(db.Integer)
    realized_nft_price = db.Column(db.Float)
    fill_sa = db.Column(db.Float)
    fill_ba = db.Column(db.Float)
    fill_sb = db.Column(db.Float)
    fill_bb = db.Column(db.Float)
    token_IDAS = db.Column(db.Integer)

    def __init__(self,
                 tx_id,
                 nft_id,
                 full_nft_id,
                 collection_id,
                 tx_typename,
                 from_fee,
                 from_fee_token_id,
                 to_fee,
                 to_fee_token_id,
                 amount,
                 block_id,
                 block_timestamp,
                 from_acct_id,
                 to_acct_id,
                 realized_nft_price,
                 fill_sa,
                 fill_ba,
                 fill_sb,
                 fill_bb,
                 token_IDAS
                 ):

        self.tx_id = tx_id
        self.nft_id = nft_id
        self.full_nft_id = full_nft_id
        self.collection_id = collection_id
        self.tx_typename = tx_typename
        self.from_fee = from_fee
        self.from_fee_token_id = from_fee_token_id
        self.to_fee = to_fee
        self.to_fee_token_id = to_fee_token_id
        self.amount = amount
        self.block_id = block_id
        self.block_timestamp = block_timestamp
        self.from_acct_id = from_acct_id
        self.to_acct_id = to_acct_id
        self.realized_nft_price = realized_nft_price
        self.fill_sa = fill_sa
        self.fill_ba = fill_ba
        self.fill_sb = fill_sb
        self.fill_bb = fill_bb
        self.token_IDAS = token_IDAS


class Account(db.Model):

    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # , autoincrement=False)
    address = db.Column(db.String)
    account_type = db.Column(db.String)

    def __init__(self, id, address, account_type):
        self.id = id
        self.address = address
        self.account_type = account_type


###############################
# Below to be added for Wallets
###############################
#
# class TransactionAll(db.Model):
#
#     __tablename__ = "transaction_all"
#
#     id = db.Column(db.String, primary_key=True, autoincrement=False)  # Tx id This should be the real primary key (or the Loopring internal tx id)
#     nft_internal = db.Column(db.Integer)  # probably should make this a nft int (internal)
#     nft_id = db.Column(db.String)
#     tx_typename = db.Column(db.String)
#     from_fee = db.Column(db.Float)
#     amount = db.Column(db.Float)
#     block_id = db.Column(db.Integer)
#     block_timestamp = db.Column(db.Integer)
#     from_acct_id = db.Column(db.Integer)
#     from_acct_address = db.Column(db.String)
#     from_acct_typename = db.Column(db.String)
#     to_acct_id = db.Column(db.Integer)
#     to_acct_address = db.Column(db.String)
#     to_acct_typename = db.Column(db.String)
#     fee_token_id = db.Column(db.Integer)
#     fee_token_symbol = db.Column(db.String)
#     fee_token_decimals = db.Column(db.Integer)
#     realized_nft_price = db.Column(db.Float)
#     fee_buyer = db.Column(db.Float)
#     fee_seller = db.Column(db.Float)
#     fill_sa = db.Column(db.Float)
#     fill_ba = db.Column(db.Float)
#     fill_sb = db.Column(db.Float)
#     fill_bb = db.Column(db.Float)
#     token_IDAS = db.Column(db.Integer)
#     token_id = db.Column(db.Integer)
#     token_symbol = db.Column(db.String)
#     token_decimals = db.Column(db.Integer)
#
#
#     def __init__(self, nft_id, full_nft_id, collection_id, collection_address):
#
#         self.id =id
#         self.nft_id = nft_id
#         self.full_nft_id = full_nft_id
#         # self.tx_typename = tx_typename
#         # self.from_fee = from_fee
#         # self.amount = amount
#         # self.block_id = block_id
#         # self.block_timestamp = block_timestamp
#         # self.from_acct_id = from_acct_id
#         # self.from_acct_address = from_acct_address
#         # self.from_acct_typename = from_acct_typename
#         # self.to_acct_id = to_acct_id
#         # self.to_acct_address = to_acct_address
#         # self.to_acct_typename = to_acct_typename
#         # self.fee_token_id = fee_token_id
#         # self.fee_token_symbol = fee_token_symbol
#         # self.fee_token_decimals = fee_token_decimals
#         # self.realized_nft_price = realized_nft_price
#         # self.fee_buyer = fee_buyer
#         # self.fee_seller = fee_seller
#         # self.fill_sa = fill_sa
#         # self.fill_ba = fill_ba
#         # self.fill_sb = fill_sb
#         # self.fill_bb = fill_bb
#         # self.token_IDAS = token_IDAS
#         # self.token_id = token_id
#         # self.token_symbol = token_symbol
#         # self.token_decimals = token_decimals
#
#
# class AccountDetails(db.Model):
#
#     __tablename__ = "account_details"
#     account_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
#     created_at_utc = db.Column(db.Date)
#     last_tx = db.Column(db.Date)
#     public_key = db.Column(db.String)
