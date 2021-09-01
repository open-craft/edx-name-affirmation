3. Using Signals for Name Affirmation
-------------------------------------

Status
------

Accepted

Context
-------

The lifecycle of a `VerifiedName` object should be affected by the status of the associated ID verification or proctored exam attempt. `VerifiedName`
creation and any updates to a record should be driven by status changes to the record's corresponding ID verification or proctored exam attempt.
It should also be noted that there is not a direct correlation between the statuses for a `VerifiedName` and the statuses used by the
ID Verification and Proctoring services, so some level of translation has to occur between the services.

Options
-------
* Import Name Affirmation python API into ID Verification and Proctoring services

  * Spreads out name affirmation logic across multiple services
  * Services are both pushing to and pulling information from name affirmation
* Have ID Verification and Proctoring services send celery events for Name Affirmation to receive

  * Better boundaries between services, and name affirmation logic could be contained within the Name Affirmation plugin.
  * Celery is not currently set up in `edx-proctoring`, and would require work to configure it.
* Define Django signals in both the ID Verification and Proctoring services and signal handlers in the Name Affirmation plugin.

  * Take advantage of edx-django-utils to hookup the signals and receivers across the services.
  * Better boundaries between services, and name affirmation logic could be contained within the name affirmation service.

Decision
--------

* Use Django Plugin Signals to send and receive info about ID verification and proctored exam attempts for name affirmation to consume.

  * The signals that each service sends should be defined within that service. These signals should be "receiver agnostic", meaning
    that the signal should not be aware that it is going to be used by name affirmation and therefore does not contain any name affirmation logic.
  * Signal receivers will be defined in the Name Affirmation plugin. The receivers will be responsible for any status translation logic, and
    for deciding when a `VerifiedName` record should be created or updated.
* This allows the services sending signals to be decoupled from the name affirmation service, and for all name affirmation logic to be contained within the Name Affirmation plugin.


Consequences
------------

* IDV and proctoring services will emit signals each time an IDV or exam attempt record is updated.
* Name Affirmation plugin is the only place that is responsible for deciding when to update or create a `VerifiedName`.
* Any new services that will need to affect updates to a VerifiedName record should be configured as a plugin signal, and a
  corresponding signal handler should be defined in name affirmation.

References
----------

* `Information on django plugin signals <https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/plugins/README.rst>`_
