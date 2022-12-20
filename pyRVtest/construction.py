"""Data construction."""

import contextlib
import os
from typing import Mapping, Optional

import numpy as np
from numpy.linalg import inv
from pyblp.utilities.basics import Array, RecArray

from . import options


def build_markups(
        products: RecArray, demand_results: Mapping, model_downstream: Array, ownership_downstream: Array,
        model_upstream: Optional[Array] = None, ownership_upstream: Optional[Array] = None,
        vertical_integration: Optional[Array] = None, custom_model_specification: Optional[dict] = None,
        user_supplied_markups: Optional[Array] = None) -> Array:
    r"""This function computes markups for a large set of standard models. These include:
            - standard bertrand with ownership matrix based on firm id
            - price setting with arbitrary ownership matrix (e.g. profit weight model)
            - standard cournot with ownership matrix based on firm id
            - quantity setting with arbitrary ownership matrix (e.g. profit weight model)
            - monopoly
            - bilateral oligopoly with any combination of the above models upstream and downstream
            - bilateral oligopoly as above but with subset of products vertically integrated
            - any of the above with consumer surplus weights (maybe)  # TODO: do we have this?

        Parameters
        ----------
        products : `RecArray`
            product_data used for pytBLP demand estimation
        demand_results : `Mapping`
            results structure from pyBLP demand estimation
        model_downstream: Array
            Can be one of ['bertrand', 'cournot', 'monopoly', 'perfect_competition']. If model_upstream not specified,
            this is a model without vertical integration.
        ownership_downstream: Array
            (optional, default is standard ownership) ownership matrix for price or quantity setting
        model_upstream: Optional[Array]
            Can be one of ['none' (default), bertrand', 'cournot', 'monopoly', 'perfect_competition']. Upstream firm's
            model.
        ownership_upstream: Optional[Array]
            (optional, default is standard ownership) ownership matrix for price or quantity setting of upstream firms
        vertical_integration: Optional[Array]
            (optional, default is no vertical integration) vector indicating which product_ids are vertically integrated
            (ie store brands)
        custom_model_specification: Optional[dict]
            (optional, default is None) dictionary containing a custom markup formula and the name of the formula
        user_supplied_markups: Optional[array]
            (optional, default is None) vector containing user-computed markups

        Returns
        -------
        `ndarray`
            The built matrix.

        Notes
        _____
        For models without vertical integration, firm_ids must be defined in product_data for vi models, and
        firm_ids_upstream and firm_ids (=firm_ids_downstream) must be defined.
    """
    # TODO: add error if model is other custom model and custom markup can't be None

    # initialize
    N = np.size(products.prices)
    with contextlib.redirect_stdout(open(os.devnull, 'w')):
        ds_dp = demand_results.compute_demand_jacobians()
    number_models = len(model_downstream)
    markets = np.unique(products.market_ids)

    # TODO: is there a better way to initialize these?
    # initialize markups
    markups = [None] * number_models
    markups_upstream = [None] * number_models
    markups_downstream = [None] * number_models
    for i in range(number_models):
        markups_downstream[i] = np.zeros((N, 1), dtype=options.dtype)
        markups_upstream[i] = np.zeros((N, 1), dtype=options.dtype)

    # compute markups market-by-market
    for i in range(number_models):
        if user_supplied_markups[i] is not None:
            markups[i] = user_supplied_markups[i]
            markups_downstream[i] = user_supplied_markups[i]
        else:
            for t in markets:
                index_t = np.where(demand_results.problem.products['market_ids'] == t)[0]
                shares_t = products.shares[index_t]
                retailer_response_matrix = ds_dp[index_t]
                retailer_response_matrix = retailer_response_matrix[:, ~np.isnan(retailer_response_matrix).all(axis=0)]

                # if there is an upstream model, compute demand hessians
                if not (model_upstream[i] is None):
                    with contextlib.redirect_stdout(open(os.devnull, 'w')):
                        d2s_dp2_t = demand_results.compute_demand_hessians(market_id=t)

                # compute downstream markups for model i market t
                markups_downstream[i], retailer_ownership_matrix = compute_markups(
                    index_t, model_downstream[i], ownership_downstream[i], retailer_response_matrix, shares_t,
                    markups_downstream[i], custom_model_specification[i], markup_type='downstream'
                )
                markups_t = markups_downstream[i][index_t]

                # compute upstream markups (if applicable) following formula in Villas-Boas (2007)
                if not (model_upstream[i] is None):

                    # construct the matrix of derivatives with respect to prices for other manufacturers
                    J = len(shares_t)
                    g = np.zeros((J, J))
                    for j in range(J):
                        g[j] = np.transpose(markups_t) @ (retailer_ownership_matrix * d2s_dp2_t[:, j, :])

                    # solve for derivatives of all prices with respect to the wholesale prices
                    H = np.transpose(retailer_ownership_matrix * retailer_response_matrix)
                    G = retailer_response_matrix + H + g
                    delta_p = inv(G) @ H

                    # solve for matrix of cross-price elasticities of derived demand and the effects of cost
                    #   pass-through
                    manufacturer_response_matrix = np.transpose(delta_p) @ retailer_response_matrix

                    # compute upstream markups
                    markups_upstream[i], manufacturer_ownership_matrix = compute_markups(
                        index_t, model_upstream[i], ownership_upstream[i], manufacturer_response_matrix, shares_t,
                        markups_upstream[i], custom_model_specification[i], markup_type='upstream'
                    )

    # compute total markups as sum of upstream and downstream markups, taking into account vertical integration
    for i in range(number_models):
        if user_supplied_markups[i] is None:
            if vertical_integration[i] is None:
                vi = np.ones((N, 1))
            else:
                vi = (vertical_integration[i] - 1) ** 2
            markups[i] = markups_downstream[i] + vi * markups_upstream[i]

    return markups, markups_downstream, markups_upstream


def compute_markups(
        index, model_type, type_ownership_matrix, response_matrix, shares, markups, custom_model_specification,
        markup_type):
    """ Compute markups for some standard models including Bertrand, Cournot, monopoly, and perfect competition. Allow
    user to pass in their own markup function as well.
    """
    if (markup_type == 'downstream') or (markup_type == 'upstream' and model_type is not None):

        # construct ownership matrix
        ownership_matrix = type_ownership_matrix[index]
        ownership_matrix = ownership_matrix[:, ~np.isnan(ownership_matrix).all(axis=0)]

        # compute markups based on specified model
        if model_type == 'bertrand':
            markups[index] = -inv(ownership_matrix * response_matrix) @ shares
        elif model_type == 'cournot':
            markups[index] = -(ownership_matrix * inv(response_matrix)) @ shares
        elif model_type == 'monopoly':
            markups[index] = -inv(response_matrix) @ shares
        elif model_type == 'perfect_competition':
            markups[index] = np.zeros((len(shares), 1))
        else:
            if custom_model_specification is not None:
                custom_model, custom_model_formula = next(iter(custom_model_specification.items()))
                markups[index] = eval(custom_model_formula)
                model_type = custom_model  # TODO: have custom model name in table output

    return markups, ownership_matrix
