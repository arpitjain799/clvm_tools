from clvm import KEYWORD_TO_ATOM


# (lambda x (* x x)) => (quote (* (a) (a)))
# lambda_op
# (symbol_replace sexp symbol_table)
# (symbol_table sexp) => symbol_table

ARGS_KW = KEYWORD_TO_ATOM["a"]
FIRST_KW = KEYWORD_TO_ATOM["f"]
REST_KW = KEYWORD_TO_ATOM["r"]
CONS_KW = KEYWORD_TO_ATOM["c"]
QUOTE_KW = KEYWORD_TO_ATOM["q"]


def symbol_table_sexp(sexp, so_far=[ARGS_KW]):
    if sexp.nullp():
        return sexp

    if not sexp.listp():
        return sexp.to([[sexp, so_far]])

    r = []
    for pair in symbol_table_sexp(sexp.first(), [
            CONS_KW, FIRST_KW, [CONS_KW, so_far, []]]).as_iter():
        _ = pair.first()
        node = pair.rest().first()
        r.append(_.to([_, node]))
    for pair in symbol_table_sexp(sexp.rest(), [
            CONS_KW, REST_KW, [CONS_KW, so_far, []]]).as_iter():
        _ = pair.first()
        node = pair.rest().first()
        r.append(_.to([_, node]))

    return sexp.to(r)


def symbol_replace(sexp, symbol_table, eval_f, root_node):
    if sexp.nullp():
        return sexp

    if not sexp.listp():
        for pair in symbol_table.as_iter():
            symbol = pair.first().as_atom()
            if symbol == sexp.as_atom():
                prog = pair.rest().first()
                r = eval_f(eval_f, prog, root_node)
                return r
        return sexp

    operator = sexp.first()
    if not operator.listp() and operator.as_atom() == QUOTE_KW:
        return sexp

    return sexp.to([operator] + [
        symbol_replace(_, symbol_table, eval_f, root_node)
        for _ in sexp.rest().as_iter()])


def compile_lambda_op(args, eval_f):
    symbol_table_args = eval_f(eval_f, args.first(), args.null())
    symbol_table = symbol_table_sexp(symbol_table_args)
    root_node = args.to([ARGS_KW])
    code_args = eval_f(eval_f, args.rest().first(), args.null())
    expansion = symbol_replace(
        code_args, symbol_table, eval_f, root_node)
    return args.to([b"compile_op", [QUOTE_KW, expansion]])
