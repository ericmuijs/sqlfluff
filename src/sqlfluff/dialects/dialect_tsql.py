"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    StartsWith,
)

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.dialects.tsql_keywords import RESERVED_KEYWORDS

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Update only RESERVED Keywords
# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)


tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([a-zA-Z][^\[\]]*)*\]",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
)

tsql_dialect.replace(
    # Below delimiterstatement might need to be removed in the future as delimiting
    # is optional with semicolon and GO is a end of statement indicator.
    DelimiterSegment=OneOf(
        Sequence(Ref("SemicolonSegment"), Ref("GoStatementSegment")),
        Ref("SemicolonSegment"),
        Ref("GoStatementSegment"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
)


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    parse_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("CreateProcedureStatementSegment"),
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
        ],
    )

@tsql_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` statement.
    
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("UNIQUE", optional=True),
        OneOf("CLUSTERED","NONCLUSTERED", optional=True),
        "INDEX",
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
    )


@tsql_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = StartsWith("DECLARE")
    parse_grammar = Sequence(
        "DECLARE",
        Delimited(Ref("ParameterNameSegment")),
        Ref("DatatypeSegment"),
        Sequence(
            Ref("EqualsSegment"),
            OneOf(
                Ref("LiteralGrammar"),
                Bracketed(Ref("SelectStatementSegment")),
                Ref("BareFunctionSegment"),
                Ref("FunctionSegment"),
            ),
            optional=True,
        ),
    )

@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifers can be matched.
    """

    type = "object_reference"
    # match grammar (don't allow whitespace)
    match_grammar: Matchable = Delimited(
        Ref("SingleIdentifierGrammar"),
        delimiter=OneOf(
            Ref("DotSegment"), Sequence(Ref("DotSegment"), Ref("DotSegment"))
        ),
        allow_gaps=False,
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities.

    GO statements are not part of the TSQL language. They are used to signal batch statements
    so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Updated for Transact-SQL to allow bracketed data types with bracketed schemas.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment()
class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
            "NEXT",
            "VALUE",
            "FOR",
            Ref("ObjectReferenceSegment"),
        )


@tsql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-ELSE-END IF statement.

   https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(Ref("IfNotExistsGrammar"),Ref("SelectStatementSegment")),
            Sequence(Ref("IfExistsGrammar"),Ref("SelectStatementSegment")),
            "IF",
            Ref("ExpressionSegment"),           
        ),
        Ref("StatementSegment"),
        Sequence("ELSE", Ref("StatementSegment"), optional=True),
    )


@tsql_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                    Ref("NextValueSequenceSegment"),
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI though.

    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Adjusted from ansi as Transact SQL does not seem to have the QuotedLiteralSegmentand Language.
    Futhermore the body can contain almost anything like a function with table output.
    """

    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence("AS", Sequence(Anything()))


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = Sequence("AS", 
        OneOf(
            Delimited(Ref("StatementSegment"),delimiter=Ref("DelimiterSegment")),
            Sequence("BEGIN", Delimited(Ref("StatementSegment"),delimiter=Ref("DelimiterSegment")),"END"),
        ))


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SelectableGrammar"),
    )
