if boot.GetValue('cryptoPack', 'Placebo') == 'CryptoAPI':
    import binascii
    import blue
    import blue.crypto
    import macho
    public = blue.marshal.Load(binascii.a2b_hex('7e0000000013540602000000a40000525341310002000001000100654d236038223e245f8d01269b5c9e6636333756f7977ce4a7f06f344d52ca840fba60bb76cf77d1ec5dfd3dbec37b5f3a4c8c7f87a8b7433b6c69f9d45afec5'))
    key = blue.crypto.CryptImportKey(macho.GetCryptoContext(), public, None, 0)
    version = macho.CryptoHash(public)
    exports = {'macho.publicKey': key,
     'macho.publicKeyVersion': version}

