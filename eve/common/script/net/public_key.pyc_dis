#Embedded file name: c:/depot/games/branches/release/EVE-TRANQUILITY/eve/common/script/net/public_key.py
if boot.GetValue('cryptoPack', 'Placebo') == 'CryptoAPI':
    import binascii
    import blue
    import blue.crypto
    import macho
    public = blue.marshal.Load(binascii.a2b_hex('7e0000000013540602000000a4000052534131000200000100010059bde0a7f3ceb310981e9afb53a7cd32c9701e8bd645af134d07746cabe5e54a676af77c23574637f5bd371a4233616f9f0c89cb6385177445992e773f4f6cc6'))
    key = blue.crypto.CryptImportKey(macho.GetCryptoContext(), public, None, 0)
    version = macho.CryptoHash(public)
    exports = {'macho.publicKey': key,
     'macho.publicKeyVersion': version}