"""Reputation context: a freelancer's trust standing, derived from sealed deals.

Reputation is *earned*, never declared. It is computed deterministically from the
Referral aggregate: a deal only counts once both parties have signed (it carries an
``attribution_hash``), completion raises standing, and an open dispute lowers it. This
is the pure, framework-free showcase logic of the trust network, mirroring the
billing schedule service.
"""
