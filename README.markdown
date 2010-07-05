Pysty
=====

A command line interface for working with RESTful services.

Requirements
------------
 - Python 2.6
 - pygments

Features
--------
 - Supports GET, POST, PUT and DELETE
 - Readline support with tab-completion and reverse search history
 - Automatic cookie session handling
 - Syntax highlighting for all types of markup or data formats, e.g. JSON, HTML, etc.
 - Pretty printing JSON
 - Transparently decompress gzip responses

Usage
-----

    # pysty --base-url=http://api.stackoverflow.com
    http://api.stackoverflow.com> GET /0.9/questions
    --------------------------------------------------------------------------------
    GET http://api.stackoverflow.com/0.9/questions
    --------------------------------------------------------------------------------
    {
      "questions": [
        {
          "title": "Even Spaced Primary / Secondary Columns in Rails",
          "question_id": 3177269,
          ...
        },
        ...
      ]
    }

Once you set the `base_url`, it sticks for next time you run it:

    # pysty
    http://api.stackoverflow.com> GET /0.9/questions

By default, `pysty` sets some additional HTTP request headers for you:

    > header_list
    Content-Type application/json
    Accept application/json

But.. you can add/modify them to your needs:

    > header_set Accept application/xml


