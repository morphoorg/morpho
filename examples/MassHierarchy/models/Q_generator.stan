/*
* MC Beta Decay Spectrum Endpoint Model - Generator
* -----------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 11 January 2016
*
* Purpose:
*
* Generates endpoint (Q value) distribution.
*
*/

functions{

// Load libraries

    include_functions<-constants
    include_functions<-func_routines
    include_functions<-Q_Functions

// Finds a simplex of isotopolog fractional composition values in the form (f_T2,f_HT,f_DT, f_atomic) given parameters epsilon and kappa

    simplex find_composition(real epsilon, real kappa, real eta)
    {
        simplex[4] composition;

        composition[1] <- (2.0*epsilon - 1.0) * eta;
        composition[2] <- (2.0*(1.0-epsilon)*kappa * eta)/(1+kappa);
        composition[3] <- (2.0*(1.0-epsilon) * eta)/(1+kappa);
	composition[4] <- 1.- eta;
        return composition;
    }

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
    vector[num_iso] Q_values;          // Best-estimate endpoint values for (T2, HT, DT, and T)

    real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
    real kappa_set;     // Average ratio of HT to DT
    real eta_set;       // Average composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

    real delta_epsilon; //Uncertainty in fractional activity of source gas compared to pure T_2
    real delta_kappa; //Uncertainty in ratio of HT to DT
    real delta_eta; //Uncertainty in composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)
    real delta_theory; //Uncertainty in composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

}

transformed data{

    vector<lower=0.0>[num_iso] ;

    mass_s[1] <- tritium_atomic_mass();
    mass_s[2] <- hydrogen_atomic_mass();
    mass_s[3] <- deuterium_atomic_mass();
    mass_s[4] <- 0.0;
    
}

parameters{

    //Parameters sampled by vnormal_lp function

    real uT;
    real uS;
    
    real<lower=0.0, upper=1.0> lambda;
    simplex[num_iso] composition;
    real<lower=minKE, upper=maxKE> Q;

}

transformed parameters{

    real<lower=0.0> sigmaT;     // Total temperature variation (K)
    real<lower=0.0> temperature;   // Temperature of source gas (K)

    real<lower=0.0> Q_avg;             // Best estimate for value of Q (eV)
    real<lower=0.0> sigma_avg;         // Best estimate for value of sigmaQ (eV)
    real<lower=0.0> p_squared;         // (Electron momentum)^2 at the endpoint
    vector<lower=0.0>[num_iso] sigma_0;
    vector<lower=0.0>[num_iso] sigma;

    real epsilon;
    real kappa;
    real eta;

    real sigma_theory;

// Create distribution for each parameter

// Temperature of system

    sigmaT <- sqrt(square(deltaT_calibration) + square(deltaT_fluctuation));
    temperature <- vnormal_lp(uT, T_set, sigmaT);

// Composition and purity of gas system

    composition <- find_composition(epsilon, kappa, eta);

// Find standard deviation of endpoint distribution (eV), given normally distributed input parameters.
    
    for (i in 1:num_iso) {
        p_squared <- 2.0 * Q_values[i] * m_electron();
    	sigma_0[i] <- find_sigma(temperature, p_squared, mass_s[i], num_J, lambda);
    }
    
    sigma_theory <- vnormal_lp(uS, 0. , delta_theory);
    sigma <- sigma_0 * (1. + sigma_theory);
    
//  Take averages of Q and sigma values

    sigma_avg <- sum(composition .* sigma);
    Q_avg <- sum(composition .* Q_values);

}

model{

// Find lambda distribution

    lambda_set ~ normal(lambda, delta_lambda);
   
// Find composition distribution

    epsilon_set ~ normal(epsilon, delta_epsilon);
    kappa_set ~ normal(kappa, delta_kappa);
    eta_set ~ normal(eta, delta_eta);

//  Distribute Q value from average

    Q ~ normal(Q_avg, sigma_avg);
   
}



