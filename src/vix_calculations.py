# Packages imports
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

# Constant eta (30 days / 252 trading days)
ETA = 30.0 / 252.0

def d_func(tau: float, u: float, lambda_p: float, xi_p: float) -> float:
    """
    This is the formula for d(T-t,u)
    """
    val = 2 * lambda_p - u * xi_p**2
    denominator = u * xi_p**2 + val * np.exp(lambda_p * tau)
    return (2 * lambda_p * u) / denominator

def c_func(tau: float, u: float, lambda_p: float, theta_p: float, xi_p: float) -> float:
    """
    This is the formula for c(T-t,u)
    """
    val = 2 * lambda_p - u * xi_p**2
    
    # If val is non-positive, the formula is not well-defined
    if val <= 0:
        return np.inf

    # log_numerator = np.exp(lambda_p * tau) * val
    log_numerator = np.exp(lambda_p * tau) * (2 * lambda_p)
    log_denominator = (u * xi_p**2 + val * np.exp(lambda_p * tau))
    
    log_term = np.log(log_numerator / log_denominator)
    
    return (2 * lambda_p * theta_p / xi_p**2) * log_term


def compute_vix_futures_price(
    tau: float,
    V_t: float,
    lambda_p: float,
    theta_p: float,
    xi_p: float
) -> float:
    """
    Computes the VIX futures price
    """
    b_prime = (1 - np.exp(-lambda_p * ETA)) / lambda_p
    a_prime = theta_p * (ETA - b_prime)

    def integrand(s: float) -> float:
        """
        Defines the integrand for the VIX futures pricing formula, which is integrated over 's'.
        """
        # The argument for the Laplace transform functions is u = s * b'
        u = s * b_prime

        # Calculate the exponent l(s, tau, V_t)
        # l = s*a' + c(tau, u) + d(tau, u)*V_t
        c_val = c_func(tau, u, lambda_p, theta_p, xi_p)
        d_val = d_func(tau, u, lambda_p, xi_p)
        
        l_val = s * a_prime + c_val + d_val * V_t
        
        if np.isinf(l_val) or np.isnan(l_val):
            return 0

        return (1 - np.exp(-l_val)) / (s**1.5)

    # Perform the numerical integration from 0 to infinity
    integral_val, _ = quad(integrand, 0, np.inf, epsabs=1e-9, epsrel=1e-9, limit=200)
    
    price = (50 / np.sqrt(np.pi * ETA)) * integral_val
    return price


def analyze_parameter_sensitivity():
    """
    Analyzes how the VIX futures price depends on the model parameters
    """
    print('--- Running Parameter Sensitivity Analysis ---')

    output_dir = 'results/figures'
    os.makedirs(output_dir, exist_ok=True)

    # Case parameters for the analysis
    base_V_t = 0.04  # Corresponds to a VIX of 20
    base_tau = 0.25  # 3 months remaining
    base_params = {'lambda_p': 2.5, 'theta_p': 0.06, 'xi_p': 0.7}

    # Sensitivity to lambda (Mean-Reversion Speed)
    print('Analyzing sensitivity to lambda...')
    lambda_range = np.linspace(0.3, 5.0, 48)
    prices_lambda = [compute_vix_futures_price(base_tau, base_V_t, l, base_params['theta_p'], base_params['xi_p']) for l in lambda_range]
    
    plt.figure(figsize=(7, 5))
    plt.plot(lambda_range, prices_lambda)
    plt.title('VIX Futures Price vs. $\\lambda$ (Mean-Reversion Speed)')
    plt.xlabel('$\\lambda$')
    plt.ylabel('Futures Price')
    plt.grid(True)
    
    file_path_lambda = os.path.join(output_dir, 'vix_futures_sensitivity_lambda.png')
    plt.savefig(file_path_lambda, dpi=300, bbox_inches='tight')
    plt.close()

    # Sensitivity to theta (Long-Run Variance)
    print('Analyzing sensitivity to theta...')
    theta_range = np.linspace(0.0, 0.1, 51)
    prices_theta = [compute_vix_futures_price(base_tau, base_V_t, base_params['lambda_p'], t, base_params['xi_p']) for t in theta_range]

    plt.figure(figsize=(7, 5))
    plt.plot(theta_range, prices_theta)
    plt.title('VIX Futures Price vs. $\\theta$ (Long-Run Variance)')
    plt.xlabel('$\\theta$')
    plt.ylabel('Futures Price')
    plt.grid(True)
    
    file_path_theta = os.path.join(output_dir, 'vix_futures_sensitivity_theta.png')
    plt.savefig(file_path_theta, dpi=300, bbox_inches='tight')
    plt.close()

    # Sensitivity to xi (Volatility of Volatility)
    print('Analyzing sensitivity to xi...')
    xi_range = np.linspace(0.1, 1.50, 141)
    prices_xi = [compute_vix_futures_price(base_tau, base_V_t, base_params['lambda_p'], base_params['theta_p'], x) for x in xi_range]

    plt.figure(figsize=(7, 5))
    plt.plot(xi_range, prices_xi)
    plt.title('VIX Futures Price vs. $\\xi$ (Vol of Vol)')
    plt.xlabel('$\\xi$')
    plt.ylabel('Futures Price')
    plt.grid(True)

    file_path_xi = os.path.join(output_dir, 'vix_futures_sensitivity_xi.png')
    plt.savefig(file_path_xi, dpi=300, bbox_inches='tight')
    plt.close()
    
    print('\nSensitivity analysis complete.')


if __name__ == '__main__':
    analyze_parameter_sensitivity()