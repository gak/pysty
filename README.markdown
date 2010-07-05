Pysty
=====

A command line interface for working with RESTful services.

Usage
-----
    # pysty --base-url=http://api.stackoverflow.com
    http://api.stackoverflow.com> GET /0.9/questions
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    GET http://api.stackoverflow.com/0.9/questions None
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    {
      "questions": [
        {
          "view_count": 1,
          "question_comments_url": "/questions/3177269/comments",
          "tags": [
            "ruby-on-rails"
          ],
          "community_owned": false,
          "title": "Even Spaced Primary / Secondary Columns in Rails",
          "owner": {
            "display_name": "Kevin Sylvestre",
          },
          "question_answers_url": "/questions/3177269/answers",
          "question_id": 3177269
        },
        ...
      ]
    }

Once you set the base_url, it sticks for next time you run it:

    # pysty
    http://api.stackoverflow.com>




