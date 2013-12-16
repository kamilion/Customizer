#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Builtins module. Information about builtins of the currently running Python.

"""

from types import BuiltinFunctionType, FunctionType, GeneratorType

from nuitka import Utils

import sys


def _getBuiltinExceptionNames():
    def isExceptionName( builtin_name ):
        if builtin_name.endswith( "Error" ) or \
           builtin_name.endswith( "Exception" ):
            return True
        elif builtin_name in ( "StopIteration", "GeneratorExit", "SystemExit",
                               "NotImplemented", "KeyboardInterrupt" ):
            return True
        else:
            return False

    # Hide Python3 changes for builtin exception names
    try:
        import exceptions

        names = [
            str( name ) for name in dir( exceptions )
            if isExceptionName( name )
        ]

        values = {}

        for key in names:
            values[ key ] = getattr( exceptions, key )

        for key in dir( sys.modules[ "__builtin__" ] ):
            name = str( key )

            if isExceptionName( name ):
                names.append( key )
                values[ name ] = getattr( sys.modules[ "__builtin__" ], key )

    except ImportError:
        exceptions = {}

        for key, value in  sys.modules[ "builtins" ].__dict__.items():
            if isExceptionName( key ):
                exceptions[ key ] = value

        names = [
            key for key, value in exceptions.items()
        ]

        values = {}

        for key, value in exceptions.items():
            values[ key ] = value

    return names, values

builtin_exception_names, builtin_exception_values = _getBuiltinExceptionNames()

# Just to make sure it's covering these cases correctly.
assert "ValueError" in builtin_exception_names
assert "StopIteration" in builtin_exception_names
assert "GeneratorExit" in builtin_exception_names
assert "AssertionError" in builtin_exception_names
assert "BaseException" in builtin_exception_names
assert "Exception" in builtin_exception_names
assert "NotImplemented" in builtin_exception_names

def _getBuiltinNames():
    names = [
        str( x )
        for x in __builtins__.keys()
    ]

    for builtin_exception_name in builtin_exception_names:
        if builtin_exception_name in names:
            names.remove( builtin_exception_name )

    names.remove( "__doc__" )
    names.remove( "__name__" )
    names.remove( "__package__" )

    warnings = []

    for builtin_name in names:
        if builtin_name.endswith( "Warning" ):
            warnings.append( builtin_name )

    for builtin_name in warnings:
        names.remove( builtin_name )

    return names, warnings

builtin_names, builtin_warnings = _getBuiltinNames()

assert "__import__" in builtin_names
assert "int" in builtin_names

assert "__doc__" not in builtin_names
assert "sys" not in builtin_names

builtin_all_names = builtin_names + builtin_exception_names + builtin_warnings

def _getAnonBuiltins():
    anon_names = {
        # Strangely not Python3 types module
        "NoneType"                   : type( None ),
        "ellipsis"                   : type( Ellipsis ), # see above
        "NotImplementedType"         : type( NotImplemented ),
        "function"                   : FunctionType,
        "builtin_function_or_method" : BuiltinFunctionType,
        # Can't really have it any better way.
        "compiled_function"          : BuiltinFunctionType,
        "generator"                  : GeneratorType,
        "compiled_generator"         : GeneratorType, # see above
    }

    anon_codes = {
        "NoneType"                   : "Py_TYPE( Py_None )",
        "ellipsis"                   : "&PyEllipsis_Type",
        "NotImplementedType"         : "Py_TYPE( Py_NotImplemented )",
        "function"                   : "&PyFunction_Type",
        "builtin_function_or_method" : "&PyCFunction_Type",
        "compiled_function"          : "&Nuitka_Function_Type",
        "compiled_generator"         : "&Nuitka_Generator_Type",
    }

    if Utils.python_version < 300:
        class Temp:
            def __init__( self ):
                pass

            def method( self ):
                pass

        anon_names[ "classobj" ] = type( Temp )
        anon_codes[ "classobj" ] = "&PyClass_Type"

        anon_names[ "instance" ] = type( Temp() )
        anon_codes[ "instance" ] = "&PyInstance_Type"

        anon_names[ "instancemethod" ] = type( Temp().method )
        anon_codes[ "instancemethod" ] = "&PyMethod_Type"

    return anon_names, anon_codes

builtin_anon_names, builtin_anon_codes = _getAnonBuiltins()