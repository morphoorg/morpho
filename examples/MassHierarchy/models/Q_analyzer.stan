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

   include <- constants;
   include <- func_routines;
   include <- Q_Functions;

// Finds a simplex of isotopolog fractional composition values in the form (f_T2,f_HT,f_DT) given parameters epsilon and kappa

    vector find_composition(real epsilon, real kappa)
    {
        vector[3] composition;

        composition[1] <- (2.0*epsilon - 1.0);
        composition[2] <- (2.0*(1.0-epsilon)*kappa)/(1+kappa);
        composition[3] <- (2.0*(1.0-epsilon))/(1+kappa);
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
    vector[num_iso] Q_T_molecule;          // Best-estimate endpoint values for tritium molecule (T2, HT, DT)
    real Q_T_atom;          // Best-estimate endpoint values for atomic tritium

    real epsilon_set;   // Average fractional activity of source gas compared to pure T_2
    real kappa_set;     // Average ratio of HT to DT
    real eta_set;       // Average composition fraction of non-T (eta = 1.0 --> no T, eta = 0.0 --> all T)

    real delta_epsilon; //Uncertainty in fractional activity of source gas compared to pure T_2
    real delta_kappa; //Uncertainty in ratio of HT to DT

    int nData;     // Number of data points to be generated
    vector[nData] Q;        // Generated data: corresponding Q values (eV)
}

transformed data{

    vector<lower=0.0>[num_iso] mass_s;

    mass_s[1] <- tritium_atomic_mass();
    mass_s[2] <- hydrogen_atomic_mass();
    mass_s[3] <- deuterium_atomic_mass();
    
}

parameters{

    real<lower=0.,upper=1.> eta;
    
    real<lower=minKE,upper=maxKE> Q_mol;
    real<lower=minKE,upper=maxKE> Q_atom;
    
}

transformed parameters{

    real temperature;
    real p_squared;
    vector[num_iso] sigma_0;
    vector[num_iso] composition;

    real sigma_mol;
    real sigma_atom;

    temperature <- T_set;
    composition <- find_composition(epsilon_set, kappa_set);

//  Take averages of Q and sigma values of molecule
    
    for (i in 1:num_iso) {
        p_squared <- 2.0 * Q_T_molecule[i] * m_electron();
    	sigma_0[i] <- find_sigma(temperature, p_squared, mass_s[i], num_J, lambda_set);
    }
    sigma_mol <- sqrt(sum(composition .* sigma_0 .* sigma_0));

//  Find sigma of atomic tritium

    sigma_atom <- find_sigma(temperature, 2.0 * Q_T_atom * m_electron(), 0., 0, 0.);

}

model{

    for (n in 1:nData) {
    	increment_log_prob(log_sum_exp(log(eta) + normal_log(Q[n], Q_mol, sigma_mol),
                                   log1m(eta) + normal_log(Q[n], Q_atom, sigma_atom)));
    }
}
