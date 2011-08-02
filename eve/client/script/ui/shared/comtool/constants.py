CHANNEL_CUSTOM = 0
CHANNEL_FLEET = 3
exports = {}
for (k, v,) in locals().items():
    if k != 'exports':
        exports['chatconst.%s' % k] = v


