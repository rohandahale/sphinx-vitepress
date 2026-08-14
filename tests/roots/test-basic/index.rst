Basic Project
=============

Prose with Vue hazards: a generic type like ``List<T>`` in code, raw
angle text 1 < 2 > 0, and a template placeholder {{ mustache }} in plain text.
Inline code with a mustache: ``{{ name }}``.

.. _custom-label:

Section One
-----------

.. note::

   Notes become VitePress tip containers.

.. warning::

   Warnings stay warnings.

.. danger::

   Danger becomes a danger container.

.. admonition:: Custom Box

   Generic admonitions keep their custom title.

.. seealso::

   Cross-reference :ref:`custom-label` and the :doc:`other` page.

Code
----

.. code-block:: python

   def f(x):
       return {"a": x < 2}

A doctest block:

>>> 1 + 1
2

Math
----

Inline :math:`E = h\nu` and a block:

.. math::

   B_\nu(T) = \frac{2 h \nu^3}{c^2} \frac{1}{e^{h\nu/k_B T} - 1}

Lists and Tables
----------------

* item one
* item two

  * nested item

===== =====
Name  Value
===== =====
alpha 1
beta  2
===== =====

.. toctree::
   :hidden:

   other
