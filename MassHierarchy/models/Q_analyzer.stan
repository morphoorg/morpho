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


data{

    real minKE;             // Bounds of Q distribution in eV
    real maxKE;

    real temp;      //Temperature of source gas in Kelvin
    real lambda;    //Fraction of the T2 component of the source in the ortho (odd rotation) state
    int num_J;     // Number of rotational states to be considered (10)
    int num_iso;    //Number of isotopologs under consideration

    real composition[num_iso]; //Relative concentrations of (T2, HT, DT, T) - must sum to 1.0
                        //Should be a simplex - that's causing problems at the moment, though
    real Q_values[num_iso];          // Best-estimate endpoint values for (T2, HT, DT, and T)

    real delta_temp;  //Uncertainty in temperaturre (due to fluctuations and measurement precision) in Kelvin
    real delta_lambda; //Uncertainty in (lambda = sum(odd-rotation-state-coefficients))
    real delta_epsilon; //Uncertainty in fractional activity of source gas compared to pure T_2
    real delta_kappa; //Uncertainty in ratio of HT to DT
    real delta_eta; //Uncertainty in composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))

    int numPts;     // Number of data points to be generated
    vector[numPts] sigma;              // Generated data: number of each Q value
    vector[numPts] Q;        // Generated data: corresponding Q values (eV)
}


transformed data{
    real Q_avg;             // Best estimate for value of Q (eV)
    real p_squared;         // (Electron momentum)^2 at the endpoint
    real epsilon;           // Fractional activity of source gas compared to pure T_2
    real kappa;             // Ratio of HT to DT
    real eta;               // Composition fraction of T (eta = f_T/(f_T2+f_HT+f_DT))

    Q_avg <- 0;
    for (s in 1:num_iso){
        Q_avg <- Q_avg + composition[s]*Q_values[s];}

    p_squared <- 2*Q_avg*m_electron();

    epsilon <- (composition[1]+1.0)/2.0;

    if (composition[3] != 0.0){
        kappa <- composition[2]/composition[3];}
    else{
        kappa <- 0.0;}

    if (composition[1] + composition[2] + composition[3] != 0.0){
        eta <- composition[4]/(composition[1] + composition[2] + composition[3]);}
    else{
        kappa <- 0.0;}

}


parameters{

    real<lower=minKE, upper=maxKE> Q_extract;   // Extracted (incorrect) endpoint (eV)
    real<lower=0.0, upper=1.5> sigma_extract;     // Extracted (incorrect) standard deviation
}



transformed parameters{
    real sigma_avg;         // Best estimate, from theory, for standard deviation of Q distribution (eV)
    real delta_sigma;       // Uncertainty (1 stdev) in estimate of sigma (sigma_avg), from theory

    sigma_avg <- find_sigma(temp, p_squared, composition, num_J, lambda);
    delta_sigma <- find_delta_sigma(temp, p_squared, delta_temp, num_J, delta_lambda, composition, lambda, epsilon, kappa, delta_epsilon, delta_kappa);
    print(sigma_avg);
}



model {

    // Create distribution for each parameter (below)

    Q ~ normal(Q_extract, sigma_avg);
    sigma ~ normal(sigma_extract, delta_sigma);

}



