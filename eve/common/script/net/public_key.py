if boot.GetValue('cryptoPack', 'Placebo') == 'CryptoAPI':
    import binascii
    import blue
    import blue.crypto
    import macho
    public = blue.marshal.Load(binascii.a2b_hex('7e0000000013540602000000a40000525341310002000001000100cb53052617d2ef7fadc4682af3f7a37f0beb06ecacbba646101addb2402330a628a4aa5bfa9e1b8a26b68559f134f8be530598b58fbf82a7e2280c0ed69404d8'))
    key = blue.crypto.CryptImportKey(macho.GetCryptoContext(), public, None, 0)
    version = macho.CryptoHash(public)
    exports = {'macho.publicKey': key,
     'macho.publicKeyVersion': version}

