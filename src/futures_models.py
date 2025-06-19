# Packages imports
import os
import numpy as np
import matplotlib.pyplot as plt

def compute_variance_futures_price(
    tau: float,
    V_t: float,
    accrued_variance_input: float,
    tau_elapsed: float,
    lambda_p: float,
    theta_p: float,
    xi_p: float
) -> float:
    """
    Computes the price of a Variance Futures contract
    """
    # xi_p is not used in the calculation, as the price depends only on the
    # expected value of the variance, not its own volatility.

    if np.isclose(tau, 0): # Avoid division by zero if at expiry
        b_star = 1.0 # The limit of the expression as tau -> 0 -- L'Hôpital's Rule
    else:
        b_star = (1 - np.exp(-lambda_p * tau)) / (lambda_p * tau)
    
    a_star = theta_p * (1 - b_star)

    # Calculate the total expected future variance.
    expected_future_var = a_star * tau + b_star * tau * V_t

    # Process the accrued variance term from the input
    # The project gives the input as integral[(100*sqrt(V_u))^2 du]
    accrued_var = accrued_variance_input / 10000.0

    # Calculate the total term of the contract (T - t_0)
    total_term = tau + tau_elapsed
    if np.isclose(total_term, 0):
        return np.nan # Result is undefined if the contract has no duration

    total_integrated_variance = accrued_var + expected_future_var
    price = 10000 * total_integrated_variance / total_term

    return price

def analyze_variance_futures_sensitivity():
    """
    Analyzes how the Variance futures price depends on the model parameters
    """
    print("--- Running Variance Futures Parameter Sensitivity Analysis ---")

    output_dir = 'results/figures'
    os.makedirs(output_dir, exist_ok=True)

    # Case parameters for the analysis
    base_V_t = 0.04  # VIX = 20
    base_tau = 0.25  # 3 months remaining
    base_tau_elapsed = 0.25 # 3 months elapsed
    base_accrued_var = 10000 * base_V_t * base_tau_elapsed # Simplified assumption
    base_params = {'lambda_p': 2.5, 'theta_p': 0.06, 'xi_p': 0.7}

    # Sensitivity to lambda (Mean-Reversion Speed)
    print('Analyzing sensitivity to lambda...')
    lambda_range = np.linspace(0.3, 5.0, 48)
    prices_lambda = [compute_variance_futures_price(base_tau, base_V_t, base_accrued_var, base_tau_elapsed, l, base_params['theta_p'], base_params['xi_p']) for l in lambda_range]
    
    plt.figure(figsize=(7, 5))
    plt.plot(lambda_range, prices_lambda)
    plt.title('Variance Futures Price vs. $\\lambda$ (Mean-Reversion Speed)')
    plt.xlabel('$\\lambda$')
    plt.ylabel('Futures Price')
    plt.grid(True)
    
    file_path_lambda = os.path.join(output_dir, 'variance_futures_sensitivity_lambda.png')
    plt.savefig(file_path_lambda, bbox_inches='tight')
    plt.close()

    # Sensitivity to theta (Long-Run Variance)
    print('Analyzing sensitivity to theta...')
    theta_range = np.linspace(0.0, 0.1, 51)
    prices_theta = [compute_variance_futures_price(base_tau, base_V_t, base_accrued_var, base_tau_elapsed, base_params['lambda_p'], t, base_params['xi_p']) for t in theta_range]

    plt.figure(figsize=(7, 5))
    plt.plot(theta_range, prices_theta)
    plt.title('Variance Futures Price vs. $\\theta$ (Long-Run Variance)')
    plt.xlabel('$\\theta$')
    plt.ylabel('Futures Price')
    plt.grid(True)
    
    file_path_theta = os.path.join(output_dir, 'variance_futures_sensitivity_theta.png')
    plt.savefig(file_path_theta, bbox_inches='tight')
    plt.close()

    # Sensitivity to xi (Volatility of Volatility)
    print('Analyzing sensitivity to xi...')
    xi_range = np.linspace(0.1, 1.50, 141)
    prices_xi = [compute_variance_futures_price(base_tau, base_V_t, base_accrued_var, base_tau_elapsed, base_params['lambda_p'], base_params['theta_p'], x) for x in xi_range]

    plt.figure(figsize=(7, 5))
    plt.plot(xi_range, prices_xi)
    plt.title('Variance Futures Price vs. $\\xi$ (Vol of Vol)')
    plt.xlabel('$\\xi$')
    plt.ylabel('Futures Price')
    # Set y-axis limits to make the flat line clear, otherwise it might look jittery
    if len(prices_xi) > 0:
        plt.ylim(prices_xi[0] * 0.99, prices_xi[0] * 1.01)
    plt.grid(True)

    file_path_xi = os.path.join(output_dir, 'variance_futures_sensitivity_xi.png')
    plt.savefig(file_path_xi, bbox_inches='tight')
    plt.close()
    
    print('\nSensitivity analysis complete.')


if __name__ == '__main__':
    analyze_variance_futures_sensitivity()