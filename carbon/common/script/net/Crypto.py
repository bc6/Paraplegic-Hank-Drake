import blue
import blue.crypto
import binascii
import base64
import macho
import uthread
import log
Enter = blue.pyos.taskletTimer.EnterTasklet
Leave = blue.pyos.taskletTimer.ReturnFromTasklet
cryptoPack = boot.GetValue('cryptoPack', 'Placebo')
hashMethod = boot.GetValue('hashMethod', 'SHA')
symmetricKeyMethod = boot.GetValue('symmetricKeyMethod', '3DES')
symmetricKeyLength = boot.GetValue('symmetricKeyLength', 192)
symmetricKeyIVLength = boot.GetValue('symmetricKeyIVLength', None)
symmetricKeyMode = boot.GetValue('symmetricKeyMode', None)
asymmetricKeyLength = boot.GetValue('asymmetricKeyLength', 512)
cryptoAPI_cryptoProvider = boot.GetValue('CryptoAPISecurityProvider', blue.crypto.MS_ENHANCED_PROV)
cryptoAPI_cryptoProviderType = boot.GetValue('CryptoAPISecurityProviderType', 'RSA_FULL')
cryptoAPI_cryptoContext = None
cryptoAPI_PROV_cryptoProviderType = getattr(blue.crypto, 'PROV_' + cryptoAPI_cryptoProviderType)
cryptoAPI_CALG_hashMethod = getattr(blue.crypto, 'CALG_' + hashMethod, None)
cryptoAPI_CALG_symmetricKeyMethod = getattr(blue.crypto, 'CALG_' + symmetricKeyMethod, None)

def CryptoAPI_GetCryptoContext():
    global cryptoAPI_cryptoContext
    if cryptoAPI_cryptoContext is not None:
        return cryptoAPI_cryptoContext
    uthread.Lock('CryptoAPI_GetCryptoContext')
    try:
        if cryptoAPI_cryptoContext is not None:
            return cryptoAPI_cryptoContext
        cryptoAPI_cryptoContext = blue.crypto.CryptAcquireContext(None, cryptoAPI_cryptoProvider, cryptoAPI_PROV_cryptoProviderType, blue.crypto.CRYPT_VERIFYCONTEXT | blue.crypto.CRYPT_SILENT)

    finally:
        uthread.UnLock('CryptoAPI_GetCryptoContext')

    return cryptoAPI_cryptoContext



def CryptoAPI_CryptoHash(*args):
    timer = Enter('machoNet::CryptoAPI::CryptoHash')
    try:
        hash = blue.crypto.CryptCreateHash(cryptoAPI_cryptoContext, cryptoAPI_CALG_hashMethod, None, 0)
        blue.crypto.CryptHashData(hash, blue.marshal.Save(args), 0)
        return blue.crypto.CryptGetHashParam(hash, blue.crypto.HP_HASHVAL, 0)

    finally:
        Leave(timer)




def CryptoAPI_AsymmetricEncryption(packet):
    timer = Enter('machoNet::CryptoAPI::AsymmetricEncryption')
    try:
        data = blue.marshal.Save(packet)
        crypted = []
        cryptHowMuch = blue.crypto.CryptGetKeyParam(macho.publicKey, blue.crypto.KP_KEYLEN, 0) / 8 - 11
        for i in xrange(0, len(data), cryptHowMuch):
            seg = data[i:(i + cryptHowMuch)]
            cryptedSeg = blue.crypto.CryptEncrypt(macho.publicKey, None, True, 0, seg)
            crypted.append(cryptedSeg)

        return blue.marshal.Save(crypted)

    finally:
        Leave(timer)




def CryptoAPI_AsymmetricDecryption(cryptedPacket):
    timer = Enter('machoNet::CryptoAPI::AsymmetricDecryption')
    try:
        cryptedRequest = blue.marshal.Load(cryptedPacket)
        for i in xrange(len(cryptedRequest)):
            decryptseg = blue.crypto.CryptDecrypt(macho.privateKey, None, True, 0, cryptedRequest[i])
            if i:
                request += decryptseg
            else:
                request = decryptseg

        return blue.marshal.Load(request)

    finally:
        Leave(timer)




def CryptoAPI_Sign(data):
    timer = Enter('machoNet::CryptoAPI::Sign')
    try:
        hash = blue.crypto.CryptCreateHash(cryptoAPI_cryptoContext, cryptoAPI_CALG_hashMethod, None, 0)
        packedData = blue.marshal.Save(data)
        blue.crypto.CryptHashData(hash, packedData, 0)
        sign = blue.crypto.CryptSignHash(hash, blue.crypto.AT_KEYEXCHANGE, 0)
        return (packedData, sign)

    finally:
        Leave(timer)




def CryptoAPI_VivoxSign(data):
    timer = Enter('vivox::Sign')
    try:
        hash = blue.crypto.CryptCreateHash(cryptoAPI_cryptoContext, cryptoAPI_CALG_hashMethod, None, 0)
        blue.crypto.CryptHashData(hash, data, 0)
        sign = blue.crypto.CryptSignHash(hash, blue.crypto.AT_KEYEXCHANGE, 0)
        return base64.encodestring(sign).replace('\n', '')

    finally:
        Leave(timer)




def CryptoAPI_VivoxVerify(data, signature):
    timer = Enter('vivox::Verify')
    try:
        import cPickle
        cryptoContext = blue.crypto.CryptAcquireContext(None, blue.crypto.MS_ENHANCED_PROV, blue.crypto.PROV_RSA_FULL, blue.crypto.CRYPT_VERIFYCONTEXT | blue.crypto.CRYPT_SILENT)
        public = cPickle.loads(binascii.a2b_hex(crypto.AppGetVivoxPublicKey()))
        key = blue.crypto.CryptImportKey(cryptoContext, public, None, 0)
        sign = base64.decodestring(signature)
        hash = blue.crypto.CryptCreateHash(cryptoContext, blue.crypto.CALG_SHA, None, 0)
        blue.crypto.CryptHashData(hash, data, 0)
        return blue.crypto.CryptVerifySignature(hash, sign, key, 0)

    finally:
        Leave(timer)




def CryptoAPI_Verify(signedData):
    timer = Enter('machoNet::CryptoAPI::Verify')
    try:
        hash = blue.crypto.CryptCreateHash(cryptoAPI_cryptoContext, cryptoAPI_CALG_hashMethod, None, 0)
        blue.crypto.CryptHashData(hash, signedData[0], 0)
        return (blue.marshal.Load(signedData[0]), blue.crypto.CryptVerifySignature(hash, signedData[1], macho.publicKey, 0))

    finally:
        Leave(timer)




def CryptoAPI_CreateContext():
    return CryptoAPI_CryptoContext()



def CryptoAPI_GetRandomBytes(byteCount):
    return blue.crypto.CryptGenRandom(CryptoAPI_GetCryptoContext(), byteCount)



class CryptoAPI_CryptoContext:

    def __init__(self):
        self.securityProviderType = cryptoAPI_cryptoProviderType
        self.symmetricKey = None
        self.symmetricKeyCipher = None
        self.symmetricKeyMethod = symmetricKeyMethod
        self.symmetricKeyLength = symmetricKeyLength
        self.hashMethod = hashMethod



    def __CreateActualCipher(self, unencryptedKey, symmetricKey):
        if unencryptedKey is None:
            return blue.crypto.CryptImportKey(CryptoAPI_GetCryptoContext(), symmetricKey, macho.privateKey, 0)
        else:
            return unencryptedKey



    def Initialize(self, request = None):
        timer = Enter('machoNet::CryptoAPI::Context::Initialize')
        try:
            unencryptedKey = None
            if request is not None:
                securityProviderType = request.get('crypting_securityprovidertype', None) or cryptoAPI_cryptoProviderType
                key = request.get('crypting_sessionkey', None) or None
                keyLength = request.get('crypting_sessionkeylength', None) or symmetricKeyLength
                keyMethod = request.get('crypting_sessionkeymethod', None) or symmetricKeyMethod
                signingHashMethod = request.get('signing_hashmethod', None) or hashMethod
            else:
                securityProviderType = cryptoAPI_cryptoProviderType
                keyLength = symmetricKeyLength
                keyMethod = symmetricKeyMethod
                signingHashMethod = hashMethod
                unencryptedKey = blue.crypto.CryptGenKey(CryptoAPI_GetCryptoContext(), cryptoAPI_CALG_symmetricKeyMethod, keyLength << 16 | blue.crypto.CRYPT_EXPORTABLE)
                if symmetricKeyIVLength:
                    keyIV = CryptoAPI_GetRandomBytes(symmetricKeyIVLength / 8)
                    blue.crypto.CryptSetKeyParam(unencryptedKey, blue.crypto.KP_IV, keyIV)
                key = blue.crypto.CryptExportKey(unencryptedKey, macho.publicKey, blue.crypto.SIMPLEBLOB, 0)
            if self.securityProviderType and securityProviderType and self.securityProviderType != securityProviderType:
                return 'Security Provider Type Unacceptable - Type is %s but should be %s' % (securityProviderType, self.securityProviderType)
            else:
                if securityProviderType:
                    self.securityProviderType = securityProviderType
                if self.symmetricKeyLength and keyLength and self.symmetricKeyLength != keyLength:
                    return 'Symmetric Key Length Unacceptable - Length is %s but should be %s' % (keyLength, self.symmetricKeyLength)
                if keyLength:
                    self.symmetricKeyLength = keyLength
                if self.symmetricKeyMethod and keyMethod and self.symmetricKeyMethod != keyMethod:
                    return 'Symmetric Key Method Unacceptable - Method is %s but should be %s' % (keyMethod, self.symmetricKeyMethod)
                if keyMethod:
                    self.symmetricKeyMethod = keyMethod
                if self.hashMethod and signingHashMethod and self.hashMethod != signingHashMethod:
                    return 'Hash Method Unacceptable - Hash is %s but should be %s' % (signingHashMethod, self.hashMethod)
                if hashMethod:
                    self.hashMethod = hashMethod
                self.symmetricKey = key
                self.symmetricKeyCipher = self._CryptoAPI_CryptoContext__CreateActualCipher(unencryptedKey, self.symmetricKey)
                return {'crypting_securityprovidertype': securityProviderType,
                 'crypting_sessionkey': key,
                 'crypting_sessionkeylength': keyLength,
                 'crypting_sessionkeymethod': keyMethod,
                 'signing_hashmethod': signingHashMethod}

        finally:
            Leave(timer)




    def SymmetricDecryption(self, cryptedPacket):
        timer = Enter('machoNet::CryptoAPI::Context::SymmetricDecryption')
        try:
            return blue.crypto.CryptDecrypt(self.symmetricKeyCipher, None, True, 0, cryptedPacket)

        finally:
            Leave(timer)




    def SymmetricEncryption(self, plainPacket):
        timer = Enter('machoNet::CryptoAPI::Context::SymmetricEncryption')
        try:
            return blue.crypto.CryptEncrypt(self.symmetricKeyCipher, None, True, 0, plainPacket)

        finally:
            Leave(timer)




    def OptionalSymmetricEncryption(self, plainPacket):
        if self.symmetricKeyCipher is not None:
            return self.SymmetricEncryption(plainPacket)
        return plainPacket




def Placebo_GetRandomBytes(byteCount):
    timer = Enter('machoNet::PlaceboCrypto::GetRandomBytes')
    try:
        return '\x00' * byteCount

    finally:
        Leave(timer)




def Placebo_CryptoHash(*args):
    timer = Enter('machoNet::PlaceboCrypto::CryptoHash')
    try:
        return str(binascii.crc_hqx(blue.marshal.Save(args), 0))

    finally:
        Leave(timer)




def Placebo_CreateContext():
    return Placebo_CryptoContext()



def Placebo_Sign(data):
    return (data, 0)



def Placebo_Verify(signedData):
    return (signedData[0], signedData[1] == 0)



class Placebo_CryptoContext:

    def __init__(self):
        pass



    def Initialize(self, request = None):
        return {}



    def SymmetricDecryption(self, cryptedPacket):
        timer = Enter('machoNet::PlaceboCrypto::Context::SymmetricDecryption')
        try:
            return cryptedPacket

        finally:
            Leave(timer)




    def SymmetricEncryption(self, plainPacket):
        timer = Enter('machoNet::PlaceboCrypto::Context::SymmetricEncryption')
        try:
            return plainPacket

        finally:
            Leave(timer)




    def OptionalSymmetricEncryption(self, plainPacket):
        return plainPacket



args = blue.pyos.GetArg()
if '/generatekeys' in args:
    try:
        rot = blue.os.CreateInstance('blue.Rot')
        commonFileName = rot.PathToFilename('script:/../../common/script/net/public_key.py')
        serverFileName = rot.PathToFilename('script:/../../server/script/net/private_key.py')
        key = blue.crypto.CryptGenKey(CryptoAPI_GetCryptoContext(), blue.crypto.AT_KEYEXCHANGE, asymmetricKeyLength << 16 | blue.crypto.CRYPT_EXPORTABLE)
        public = blue.crypto.CryptExportKey(key, None, blue.crypto.PUBLICKEYBLOB, 0)
        private = blue.crypto.CryptExportKey(key, None, blue.crypto.PRIVATEKEYBLOB, 0)
        privateKey = 'if boot.GetValue("cryptoPack","Placebo") == "CryptoAPI":\n    # -----------------------\n    # CryptoAPI Encryption\n    # -----------------------\n    import binascii\n    import blue\n    import blue.crypto\n    import macho\n\n    private  = blue.marshal.Load(binascii.a2b_hex("%(private)s") )\n    key      = blue.crypto.CryptImportKey(macho.GetCryptoContext(), private, None, 0)\n    version  = macho.CryptoHash( private )\n\n    exports = {\n       "macho.privateKey"        : key,\n       "macho.privateKeyVersion" : version,\n    }\n' % {'private': binascii.b2a_hex(blue.marshal.Save(private))}
        publicKey = 'if boot.GetValue("cryptoPack","Placebo") == "CryptoAPI":\n    # -----------------------\n    # CryptoAPI Encryption\n    # -----------------------\n    import binascii\n    import blue\n    import blue.crypto\n    import macho\n\n    public   = blue.marshal.Load(binascii.a2b_hex("%(public)s") )\n    key      = blue.crypto.CryptImportKey(macho.GetCryptoContext(), public, None, 0)\n    version  = macho.CryptoHash( public )\n\n    exports = {\n       "macho.publicKey"        : key,\n       "macho.publicKeyVersion" : version\n    }\n' % {'public': binascii.b2a_hex(blue.marshal.Save(public))}
        blue.win32.AtomicFileWrite(serverFileName, privateKey.replace('\n', '\r\n'))
        blue.win32.AtomicFileWrite(commonFileName, publicKey.replace('\n', '\r\n'))
    except Exception:
        log.LogException()
    blue.pyos.Quit('Key Generation complete')
if cryptoPack == 'CryptoAPI':
    exports = {'macho.GetCryptoContext': CryptoAPI_GetCryptoContext,
     'macho.CryptoHash': CryptoAPI_CryptoHash,
     'macho.CryptoCreateContext': CryptoAPI_CreateContext,
     'macho.GetRandomBytes': CryptoAPI_GetRandomBytes,
     'macho.Sign': CryptoAPI_Sign,
     'macho.Verify': CryptoAPI_Verify}
else:
    exports = {'macho.CryptoHash': Placebo_CryptoHash,
     'macho.CryptoCreateContext': Placebo_CreateContext,
     'macho.GetRandomBytes': Placebo_GetRandomBytes,
     'macho.Sign': Placebo_Sign,
     'macho.Verify': Placebo_Verify}
exports['crypto.VivoxSign'] = CryptoAPI_VivoxSign
exports['crypto.VivoxVerify'] = CryptoAPI_VivoxVerify

