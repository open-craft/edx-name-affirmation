2. Name Affirmation as a Plugin
-------------------------------

Status
------

Accepted

Context
-------

`edx-name-affirmation` is intended to be an optional feature for the open edX community. As such, we
should allow the consuming application (in our case, `edx-platform <https://github.com/edx/edx-platform>`_)
to determine whether or not this feature should be installed.

Options
-------

**edx-platform app**

- Create a new application directly in `edx-platform`.
- This is the easiest option, but doesn't fit our purposes in order to decouple the code from platform.

**Django plugin**

- Decoupled from `edx-platform`, and better ability for open edX to opt out.
- `edx-platform` can utilize API directly from `edx-name-affirmation`.
- Release will still depend on `edx-platform`.

**IDA**

- Decoupled from `edx-platform` and better ability for open edX to opt out.
- It has a more involved setup, but would result in a faster deploy process.
- Having a separate service for such a small application may be overkill.


Decision
--------

We will initialize this project as a plugin application in order to decouple the code from the monolith,
but still be able to take advantage of the API as an installed library.


Consequences
------------

- `edx-name-affirmation` does not have to be enabled for every instance of open edX.
- `edx-name-affirmation` will not rely on `edx-platform` dependencies.
- In the same vein, `edx-name-affirmation` will not have direct access to utilities written in
  `edx-platform` or sibling plugins.

References
----------

- `Django Plugin Overview <https://github.com/edx/edx-django-utils/tree/master/edx_django_utils/plugins>`_
