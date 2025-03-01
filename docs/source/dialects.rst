.. _dialectref:

Dialects Reference
==================

SQLFluff is designed to be flexible in supporting a variety of dialects.
Not all potential dialects are supported so far, but several have been
implemented by the community. Below are a list of the currently available
dialects. Each inherits from another, up to the root `ansi` dialect.

For a canonical list of supported dialects, run the
:program:`sqlfluff dialects` command, which will output a list of the
current dialects available on your installation of SQLFluff.

.. note::

    For technical users looking to add new dialects or add new features
    to existing ones, the dependent nature of how dialects have been
    implemented is to try and reduce the amount of repetition in how
    different elements are defined. As an example, when we say that
    the :ref:`snowflake_dialect_ref` dialect *inherits* from the
    :ref:`postgres_dialect_ref` dialect this is not because there
    is an agreement between those projects which means that features
    in one must end up in the other, but that the design of the
    :ref:`snowflake_dialect_ref` dialect was heavily *inspired* by the
    postgres dialect and therefore when defining the dialect within
    sqlfuff it makes sense to use :ref:`postgres_dialect_ref` as a
    starting point rather than starting from scratch.

    Consider when adding new features to a dialect:

    - Should I be adding it just to this dialect, or adding it to
      a *parent* dialect?
    - If I'm creating a new dialect, which dialect would be best to
      inherit from?
    - Will the feature I'm adding break any *downstream* dependencies
      within dialects which inherit from this one?

.. _ansi_dialect_ref:

ANSI
----

This is the base dialect which holds most of the definitions of common
SQL commands and structures. If the dialect which you're actually using
isn't specifically implemented by SQLFluff, using this dialect is a good
place to start.

This dialect doesn't intend to be brutal in adhering to (and only to) the
ANSI SQL spec *(mostly because ANSI charges for access to that spec)*. It aims
to be a representation of vanilla SQL before any other project adds their
spin to it, and so may contain a slightly wider set of functions than actually
available in true ANSI SQL.

.. _bigquery_dialect_ref:

BigQuery
--------

The dialect for `Google BigQuery`_.

.. _`Google BigQuery`: https://cloud.google.com/bigquery/

.. _exasol_dialect_ref:

Exasol
------

The dialect for `Exasol`_. Note that currently Exasol script and functions
create statements are currently defined in a separate ``exasol_fs`` dialect.

.. _`Exasol`: https://www.exasol.com/

.. _hive_dialect_ref:

Hive
----

The dialect for `Hive`_.

.. _`Hive`: https://hive.apache.org/

.. _mysql_dialect_ref:

MySQL
-----

The dialect for `MySQL`_.

.. _`MySQL`: https://www.mysql.com/

.. _postgres_dialect_ref:

PostgreSQL
----------

This is based around the `PostgreSQL spec`_. Many other SQL instances are often
based on PostreSQL syntax. If you're running `AWS Redshift`_ or `Greenplum`_
this is the dialect to use (until someone makes a specific dialect).

.. _`PostgreSQL spec`: https://www.postgresql.org/docs/9.6/reference.html
.. _`AWS Redshift`: https://aws.amazon.com/redshift/
.. _`Greenplum`: https://greenplum.org/

.. _snowflake_dialect_ref:

Snowflake
---------

The dialect for `Snowflake`_, which has much of its syntax
inherited from :ref:`postgres_dialect_ref`.

.. _`Snowflake`: https://docs.snowflake.com/en/sql-reference.html

.. _sqlite_dialect_ref:

SQLite
------

The dialect for `SQLite`_.

.. _`SQLite`: https://www.sqlite.org/

.. _tsql_dialect_ref:

T-SQL
-----

The dialect for `T-SQL`_ (aka Transact-SQL).

.. _`T-SQL`: https://docs.microsoft.com/en-us/sql/t-sql/language-reference

.. _teradata_dialect_ref:

Teradata
--------

The dialect for `Teradata`_.

.. _`Teradata`: https://www.teradata.co.uk/
