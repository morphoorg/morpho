/*
* MC Beta Decay Spectrum Endpoint Model - Analyzer
* -----------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 11 January 2016
*
* Purpose:
*
* Constructs endpoint distribution from generated endpoint data (extracts values for Q_avg and sigma_avg)
*
*/


functions{

// Load libraries

    include_functions=constants
    include_functions=func_routines
    include_functions=Q_Functions
    
}

data{

    real minKE;             // Bounds of Q distribution in eV
    real maxKE;

    real T_set;      //Average temperature of source gas in Kelvin
    real deltaT_calibration;    //Temperature uncertainty due to calibration (K)
    real deltaT_fluctuation;    //Temperature uncertainty due to fluctuations (K)
    real deltaT_rot;    //Temperature uncertainty due to unaccounted for higher rotational states (K)

    int num_J;     // Number of rotational states to be considered (10)
    real lambda_set;    //Average fraction of T2 component of source in ortho (odd rotation) state
    real delta_lambda; //Uncertainty in (lambda = sum(odd-rotation-state-coefficients))

    int num_iso;    //Number of isotopologs under consideration
    //real composition[num_iso]; //Relative concentrations of (T2, HT, DT, T) - must sum to 1.0
    real Q_values[num_iso];          // Best-estimate endpoint values for (T2, HT, DT, and T)

    real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
    real kappa_set;     // Average ratio of HT to DT
    real eta_set;       // Average composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

    real delta_epsilon; //Uncertainty in fractional activity of source gas compared to pure T_2
    real delta_kappa; //Uncertainty in ratio of HT to DT
    real delta_eta; //Uncertainty in composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

    int numPts;     // Number of data points to be generated
    vector[numPts] sigma;              // Generated data: number of each Q value
    vector[numPts] Q;        // Generated data: corresponding Q values (eV)
}


parameters{

    //Parameters sampled by vnormal_lp function

    real Tparam1;
    real Tparam2;
    real lambda_param;
    real epsilon_param;
    real kappa_param;
    real eta_param;

    real<lower=minKE, upper=maxKE> Q_extract;   // Extracted (incorrect) endpoint (eV)
    real<lower=0.0, upper=1.5> sigma_extract;     // Extracted (incorrect) standard deviation


}



transformed parameters{

    real<lower=25., upper=35.> T0;     // Average of temperature distribution, given temp calibration (K)
    real<lower=25., upper=35.> temp;   // Temperature of source gas (K)
    real<lower=0.0> deltaT_total;      // Used only for calculation of delta_sigma, as check (K)

    real<lower=0.0> lambda;   // Fraction of T2 component of source in ortho (odd rotation) state
    real<lower=0.0> epsilon;  // Fractional activity of source gas compared to pure T_2
    real<lower=0.0> kappa;    // Ratio of HT to DT
    real<lower=0.0> eta;      // Composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))

    real<lower=0.0> composition[num_iso]; //Simplex of fractional composition of each isotopolog: (f_T2,f_HT,f_DT, f_T)
    real<lower=0.0> composition_set[num_iso]; //Used only for calculation of delta_sigma, as check

    real<lower=0.0> Q_avg;             // Best estimate for value of Q (eV)
    real p_squared;         // (Electron momentum)^2 at the endpoint

    real<lower=0.0> sigma_floating;         // Best estimate, from theory, for standard deviation of Q distribution (eV)
    real delta_sigma;       // Uncertainty (1 stdev) in estimate of sigma (sigma_avg), from theory


    // Create distribution for each parameter

    T0 = vnormal_lp(Tparam1, T_set, deltaT_calibration);
    temp = vnormal_lp(Tparam2, T0, deltaT_fluctuation);

    lambda = vnormal_lp(lambda_param, lambda_set, delta_lambda);
    epsilon = vnormal_lp(epsilon_param, epsilon_set, delta_epsilon);
    kappa = vnormal_lp(kappa_param, kappa_set, delta_kappa);
    if (delta_eta != 0.0){
        eta = vnormal_lp(eta_param, eta_set, delta_eta);}

    deltaT_total = pow(pow(deltaT_calibration, 2) + pow(deltaT_fluctuation, 2), 0.5);

    composition = find_composition(epsilon, kappa, eta, num_iso);
    composition_set = find_composition(epsilon_set, kappa_set, eta_set, num_iso);

    Q_avg = 0;
    for (s in 1:num_iso){
        Q_avg = Q_avg + composition[s]*Q_values[s];}
    p_squared = 2*Q_avg*m_electron();

    //Calculating sigma given normally distributed parameters (temp, lambda, composition)
    sigma_floating = find_sigma(temp, p_squared, composition, num_J, lambda);
    print ("temp: ", temp);
    print ("sigma: ", sigma_floating);


    //DELTA_SIGMA CALCULATION REQUIRES REVISION DUE TO ERROR WHEN CALCULATING find_delta_sigma_squared_eta
    // delta_sigma can be printed or outputted as a check. It should be very similar to the standard deviation of the generated sigma distribution.
    // delta_sigma = find_delta_sigma(T_set, p_squared, deltaT_total, num_J, delta_lambda, composition_set, lambda_set, epsilon_set, kappa_set, eta_set, delta_epsilon, delta_kappa, delta_eta);


    // Extracting sigma_extract using calculated delta_sigma and inputted data (as check)
    // sigma = vnormal_lp(sigma_param, sigma_extract, delta_sigma);
}



model {

    //Extracting average of Q distribution
    Q ~ normal(Q_extract, sigma_floating);


}



