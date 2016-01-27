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


data{

    real minKE;             // Bounds of Q distribution in eV
    real maxKE;

    real temp;      //Temperature of source gas in Kelvin
//    real p_squared; //Norm squared of change in momentum in molecular system as a result of beta-decay
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
    real<lower=0.0> dummy_parameter;
}


transformed parameters{

    real<lower=0.0> sigma_avg;         // Best estimate, from theory, for standard deviation of Q distribution (eV)
    real<lower=0.0> delta_sigma;       // Uncertainty (1 stdev) in estimate of sigma (sigma_avg), from theory
//    real<lower=0.0> delta_sigma_squared_epsilon;

    sigma_avg <- find_sigma(temp, p_squared, composition, num_J, lambda);

//    delta_sigma_squared_epsilon <- find_delta_sigma_squared_epsilon(temp, p_squared, num_J, lambda, kappa, delta_epsilon);

    delta_sigma <- find_delta_sigma(temp, p_squared, delta_temp, num_J, delta_lambda, composition, lambda, epsilon, kappa, delta_epsilon, delta_kappa);

}



model{
}


generated quantities {
    real<lower=0.0> sigma;
    real<lower=minKE, upper=maxKE> Q;

    // Generating endpoint (eV) and stdev of endpoint distribution (eV) from normal distribution
    sigma <- normal_rng(sigma_avg, delta_sigma);

    if (sigma <= 0.0){
        print(sigma);
        sigma <- 0.0001;}

    Q <- normal_rng(Q_avg, sigma);

    //print(Q, " ", sigma, " ", delta_sigma);

}







