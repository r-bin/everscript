# Return Feature

This note documents the compiler support for `return` and call result capture.

## What It Does

The compiler supports two return forms:

```everscript
return expr;
return;
```

`return expr;` stores the value in `CUSTOM_MEMORY.RETURN` and ends the function. `return;` ends the function without writing a value.

The same return slot is also used for call results, so a call can be used as an expression on the right-hand side of an assignment:

```everscript
value = some_function();
```

That pattern compiles to a call followed by reading `CUSTOM_MEMORY.RETURN` into the target.

## Compiler Notes

The feature is implemented across:

- `compiler/lexer.py`
- `compiler/parser.py`
- `compiler/ast_everscript.py`

The current implementation has one known caveat: using multiple calls in a single expression row can be fragile, because each call writes to the shared `CUSTOM_MEMORY.RETURN` slot.

## Example

```everscript
fun example() {
    result = get_value();
    if(result == 0) {
        return;
    }

    return result;
}
```