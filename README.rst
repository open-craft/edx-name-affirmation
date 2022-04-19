####################
edx-name-affirmation
####################

| |Build Status| |Coveralls|

This library contains data model and business logic to store verified 
personal information for learners of the edx-platform.
This library is designed to be a pluggable library to the edx-platform.

Overview
========

This library mainly stores various stages of a learner's verified identifying information.
The prevalent example is the learner's full name. To verify the full name, the learner
has to first initiate from UI that is part of the platform.
Here are the steps of which the PII information, for example: full name, goes through:

1. learner requests to update the name
2. learner is brought to go through ID verification process
3. learner submit the ID verification after providing supporting evidence
4. the ID Verification reviewer approves or denies the verification
5. the library receives the verdict and updates the name record in the model accordingly

The above process can also be triggered by a Proctored exam attempt, where the exam attempt status
can be the input into this library to create and update the name record's status. In this case,
the learner do not have to go through ID Verification. The proctoring process always collects ID
verification evidence.

For more context of the library, see `context`_.

Dependencies
------------

In addition to the edx-platform repository this library is installing into, the library also leverages
the `frontend-app-account`_ Micro-Frontend to capture learners' attempt to update their full name.

Installing in Docker Devstack
-----------------------------

Assuming that your ``devstack`` repo lives at ``~/edx/devstack``
and that ``edx-platform`` lives right alongside that directory, you'll want
to checkout ``edx-name-affirmation`` and have it live in ``~/edx/src/edx-name-affirmation``.
This will make it so that you can access it inside an LMS container shell
and easily make modifications for local testing.

Run ``make lms-shell`` from your ``devstack`` directory to enter a running LMS container.
Once in there, you can do the following to have your devstack pointing at a local development
version of ``edx-name-affirmation``:

.. code:: bash

    $ pushd /edx/src/edx-name-affirmation
    $ virtualenv venv/
    $ source venv/bin/activate
    $ make install
    $ make test  # optional, if you want to see that everything works
    $ deactivate
    $ pushd  # should take you back to /edx/edx-platform
    $ pip uninstall -y edx_name_affirmation
    $ pip install -e /edx/src/edx-name-affirmation

Alternatively, you can add ``./src/edx-name-affirmation`` to the edx-platform ``private.txt`` of the ``requirements`` folder
This way, when you are pip installing within edx-platform, you don't have to perform the above step again.

Enabling in LMS
---------------
Make sure your LMS settings have the Feature ``ENABLE_SPECIAL_EXAMS`` enabled.
Check your edx-platform ``lms/env`` settings file.

Disable the plugin library
--------------------------

There are two ways to disable the plugin library:

- You can uninstall the library from edx-platform.
- In the `setup.py`_, you can remove the ``entry_points`` into either ``LMS`` or ``CMS``

Development
-----------

installation and settings
=========================

Install to the python virtualenv with help from virtualenvwrapper:

.. code:: bash

    $ pip install --user virtualenvwrapper
    $ mkvirtualenv nameaffirmation

For detailed instructions on virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/install.html

Running tests
=============

From the edx-name-affirmation repo root, run the tests with the following command:

.. code:: bash

    $ make test

Running code quality check
==========================

From the edx-name-affirmation repo root, run the quality checks with the following command:

.. code:: bash

    $ make quality


Package Requirements
====================

``requirements/dev.txt`` contains a list of package dependencies which are required for this package.

``requirements/test.txt`` is used to install the same dependencies when running the tests for this package.


License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.


How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help
.. _context: ./docs/context.rst
.. _frontend-app-account: https://github.com/openedx/frontend-app-account
.. _setup.py: ./setup.py


.. |Build Status| image:: https://github.com/edx/edx-name-affirmation/workflows/Python%20CI/badge.svg?branch=main
  :target: https://github.com/edx/edx-name-affirmation/actions?query=workflow%3A%22Python+CI%22

.. |Coveralls| image:: https://coveralls.io/repos/edx/edx-name-affirmation/badge.svg?branch=main&service=github
  :target: https://coveralls.io/github/edx/edx-name-affirmation?branch=main