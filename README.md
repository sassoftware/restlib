Welcome to restlib!
===================

**Archived projet: This project is no longer under active development and was archived on 2024-07-24.**

Overview
--------

Restlib is a light-weight framework for writing rest-style APIs.  It
does not have any support for templating or database manipulation; those must be added manually.  This was done purposefully to keep the restlib library small.

A request sent to restlib will go through the following process:
  * conversion from raw simplehttpserver or mod_python requests into standard 
      Request objects
  * processRequest callbacks called, if any
  * view method to call determined by routing through a series of user-defined 
      Controllers 
  * processMethod callbacks called, if any
  * view method called - it should return a Response object
  * processResponse callbacks called, if any
  * response written to output.

Exceptions are handled by processException callback.

This arrangement is relatively simple and powerful.
