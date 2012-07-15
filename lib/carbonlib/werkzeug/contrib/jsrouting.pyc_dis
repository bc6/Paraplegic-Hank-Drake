#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\werkzeug\contrib\jsrouting.py
try:
    from simplejson import dumps
except ImportError:

    def dumps(*args):
        raise RuntimeError('simplejson required for jsrouting')


from inspect import getmro
from werkzeug.templates import Template
from werkzeug.routing import NumberConverter
_javascript_routing_template = Template(u"<% if name_parts %><% for idx in xrange(0, len(name_parts) - 1) %>if (typeof ${'.'.join(name_parts[:idx + 1])} === 'undefined') ${'.'.join(name_parts[:idx + 1])} = {};\n<% endfor %>${'.'.join(name_parts)} = <% endif %>(function (server_name, script_name, subdomain, url_scheme) {\n    var converters = ${', '.join(converters)};\n    var rules = $rules;\n    function in_array(array, value) {\n        if (array.indexOf != undefined) {\n            return array.indexOf(value) != -1;\n        }\n        for (var i = 0; i < array.length; i++) {\n            if (array[i] == value) {\n                return true;\n            }\n        }\n        return false;\n    }\n    function array_diff(array1, array2) {\n        array1 = array1.slice();\n        for (var i = array1.length-1; i >= 0; i--) {\n            if (in_array(array2, array1[i])) {\n                array1.splice(i, 1);\n            }\n        }\n        return array1;\n    }\n    function split_obj(obj) {\n        var names = [];\n        var values = [];\n        for (var name in obj) {\n            if (typeof(obj[name]) != 'function') {\n                names.push(name);\n                values.push(obj[name]);\n            }\n        }\n        return {names: names, values: values, original: obj};\n    }\n    function suitable(rule, args) {\n        var default_args = split_obj(rule.defaults || {});\n        var diff_arg_names = array_diff(rule.arguments, default_args.names);\n\n        for (var i = 0; i < diff_arg_names.length; i++) {\n            if (!in_array(args.names, diff_arg_names[i])) {\n                return false;\n            }\n        }\n\n        if (array_diff(rule.arguments, args.names).length == 0) {\n            if (rule.defaults == null) {\n                return true;\n            }\n            for (var i = 0; i < default_args.names.length; i++) {\n                var key = default_args.names[i];\n                var value = default_args.values[i];\n                if (value != args.original[key]) {\n                    return false;\n                }\n            }\n        }\n\n        return true;\n    }\n    function build(rule, args) {\n        var tmp = [];\n        var processed = rule.arguments.slice();\n        for (var i = 0; i < rule.trace.length; i++) {\n            var part = rule.trace[i];\n            if (part.is_dynamic) {\n                var converter = converters[rule.converters[part.data]];\n                var data = converter(args.original[part.data]);\n                if (data == null) {\n                    return null;\n                }\n                tmp.push(data);\n                processed.push(part.name);\n            } else {\n                tmp.push(part.data);\n            }\n        }\n        tmp = tmp.join('');\n        var pipe = tmp.indexOf('|');\n        var subdomain = tmp.substring(0, pipe);\n        var url = tmp.substring(pipe+1);\n\n        var unprocessed = array_diff(args.names, processed);\n        var first_query_var = true;\n        for (var i = 0; i < unprocessed.length; i++) {\n            if (first_query_var) {\n                url += '?';\n            } else {\n                url += '&';\n            }\n            first_query_var = false;\n            url += encodeURIComponent(unprocessed[i]);\n            url += '=';\n            url += encodeURIComponent(args.original[unprocessed[i]]);\n        }\n        return {subdomain: subdomain, path: url};\n    }\n    function lstrip(s, c) {\n        while (s && s.substring(0, 1) == c) {\n            s = s.substring(1);\n        }\n        return s;\n    }\n    function rstrip(s, c) {\n        while (s && s.substring(s.length-1, s.length) == c) {\n            s = s.substring(0, s.length-1);\n        }\n        return s;\n    }\n    return function(endpoint, args, force_external) {\n        args = split_obj(args);\n        var rv = null;\n        for (var i = 0; i < rules.length; i++) {\n            var rule = rules[i];\n            if (rule.endpoint != endpoint) continue;\n            if (suitable(rule, args)) {\n                rv = build(rule, args);\n                if (rv != null) {\n                    break;\n                }\n            }\n        }\n        if (rv == null) {\n            return null;\n        }\n        if (!force_external && rv.subdomain == subdomain) {\n            return rstrip(script_name, '/') + '/' + lstrip(rv.path, '/');\n        } else {\n            return url_scheme + '://'\n                   + (rv.subdomain ? rv.subdomain + '.' : '')\n                   + server_name + rstrip(script_name, '/')\n                   + '/' + lstrip(rv.path, '/');\n        }\n    };\n})")

def generate_map(map, name = 'url_map'):
    map.update()
    rules = []
    converters = []
    for rule in map.iter_rules():
        trace = [ {'is_dynamic': is_dynamic,
         'data': data} for is_dynamic, data in rule._trace ]
        rule_converters = {}
        for key, converter in rule._converters.iteritems():
            js_func = js_to_url_function(converter)
            try:
                index = converters.index(js_func)
            except ValueError:
                converters.append(js_func)
                index = len(converters) - 1

            rule_converters[key] = index

        rules.append({u'endpoint': rule.endpoint,
         u'arguments': list(rule.arguments),
         u'converters': rule_converters,
         u'trace': trace,
         u'defaults': rule.defaults})

    return _javascript_routing_template.render({'name_parts': name and name.split('.') or [],
     'rules': dumps(rules),
     'converters': converters})


def generate_adapter(adapter, name = 'url_for', map_name = 'url_map'):
    values = {u'server_name': dumps(adapter.server_name),
     u'script_name': dumps(adapter.script_name),
     u'subdomain': dumps(adapter.subdomain),
     u'url_scheme': dumps(adapter.url_scheme),
     u'name': name,
     u'map_name': map_name}
    return u'var %(name)s = %(map_name)s(\n    %(server_name)s,\n    %(script_name)s,\n    %(subdomain)s,\n    %(url_scheme)s\n);' % values


def js_to_url_function(converter):
    if hasattr(converter, 'js_to_url_function'):
        data = converter.js_to_url_function()
    else:
        for cls in getmro(type(converter)):
            if cls in js_to_url_functions:
                data = js_to_url_functions[cls](converter)
                break
        else:
            return 'encodeURIComponent'

    return '(function(value) { %s })' % data


def NumberConverter_js_to_url(conv):
    if conv.fixed_digits:
        return u"var result = value.toString();\nwhile (result.length < %s)\n    result = '0' + result;\nreturn result;" % conv.fixed_digits
    return u'return value.toString();'


js_to_url_functions = {NumberConverter: NumberConverter_js_to_url}