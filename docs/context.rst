###########
The Context
###########

Why
===

Problem
-------

Around the beginning of calendar year 2021, it was recognized within edX that the ID Verification process we
force the learner through, was not aligning with the mission of wider educational access. edX wants to trusting
the learner and assuming good intent. We wanted to reduce the barrier to entry for being a paying leaner on edX.
We should only require ID Verification on a minimal set of learners that want to change the name on their certificates.
Specific examples of ID verification challenges were (in no particular order):

- ID Verification vendors do not support a wide range of languages. Asian students had a hard time getting verified
- ID Verification process has a greater than 20% denial rate. This introduced a lot of support issues and learners pain
- Before proctoring exams, we would require ID Verification. This means learners has to provide PII evidence
  twice before exams. Furthermore, learners who has trouble with ID Verification process sometimes lost the chance to take the exams
- edX collecting learners verification documents is at security risk of hacking and leaking.
- The cost of ID verification process on edX is trending higher as the number of active paying learners grow


Solution
--------

It was proposed by edX product management that we should create a newer and more lightweight process to replace
ID Verification process for all paying learners. The design was to ask learner to go through honor code signature.
The honor code is captured by the django app agreements_.
In addition to the honor code signature, if the learners who fits the following criteria, we would trigger ID Verification:

- Has a downloadable course certificate
- The learner changes more than 1 character in their profile name,
  or they have already changed their profile name 3 times 

Furthermore, if the learner is going through Proctoring exams, the full name provided and verified as part of
the proctoring process, will be saved as a verified name in this library.

Timeline
--------
The solution was designed summer of 2021 and implemented in fall and winter of 2022. On Jan 19th, 2022, learners on
edx.org was no longer required to go through ID verification to get their certificates.


.. _agreements: https://github.com/openedx/edx-platform/tree/8070dd9be000da3fac86be19b5f0274f3d073630/openedx/core/djangoapps/agreements