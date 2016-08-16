/*
* MC Neutrino Mass and Beta Decay Model - Mass Analyzer (no spectrum)
* -------------------------------------------------------------------
* Author: Talia Weiss <tweiss@mit.edu>
*
* Date: 10 August 2016
*
* Purpose:
*
* Constructs neutrino mass model in Stan given an input distribution
* for either m_beta or m_s=m1+m2+m3.
*
* Sources for the data used as priors are given in data/experiment_key.txt.
*
*/


/*
* To do:
*
* Determine whether m_beta is impacting outcome.
* Write asymmetric "gaussian" function and incorporate..
* Incorporate covariances: "multi-gp."
* Use Bernoulli function to account for past experiments'
*   preference towards a hierarchy.
* 
*/



functions{

	// Load libraries

	include=constants;
    	include=func_routines;
    	include=neutrino_mass_functions;

}


data{

	int nExp_th12;			// Number of experiments from which neutrino
	int nExp_th13;    		// parameter distributions are inputted
	int nHierarchyDep_th13;
	int nExp_m21;
	int nExp_m32;	

	vector[nExp_th12] sin2_th12_means;	// Mean values from each experiment

	vector[nExp_th12] sin2_th12_sigmas;  	// Standard dev values from each experiment

	vector[nExp_th13] sin2_th13_means;
	vector[nExp_th13] sin2_th13_sigmas;
	vector[nHierarchyDep_th13] sin2_th13_means_NH;
	vector[nHierarchyDep_th13] sin2_th13_means_IH;
	vector[nHierarchyDep_th13] sin2_th13_sigmas_NH;
	vector[nHierarchyDep_th13] sin2_th13_sigmas_IH;	

	vector[nExp_m21] delta_m21_means;
	vector[nExp_m21] delta_m21_sigmas;

	vector[nExp_m32] delta_m32_means_NH;
	vector[nExp_m32] delta_m32_means_IH;
	vector[nExp_m32] delta_m32_sigmas_NH;
	vector[nExp_m32] delta_m32_sigmas_IH;

	real m_beta_squared_mean;	// m_beta_squared = sum(U_{e,i}^2*m_i^2)
	real m_beta_squared_sigma;

	real m_s_mean;			// m_s = sum(m_i)
	real m_s_sigma;

	int use_m_beta;			// 0 -> False, 1 -> True
	int use_m_s;
}


parameters{

	real<lower=0.0, upper=1.0> sin2_th12;
	real<lower=0.0, upper=1.0> sin2_th13;

	vector<lower=0.0, upper=1.5>[3] nu_mass;
}


transformed parameters{

	real delta_m32_with_sign;	   // Sign indicates prefered hierarchy
	real<lower=0.0> min_mass;
	vector<lower=0.0>[3] Ue_squared;   // Squares of PMNS matrix elements U_e
	real delta_m21;
	real<lower=0.0> delta_m32;
	real m_beta_squared;
	real m_beta;
	real m_s;

	delta_m21 = square(nu_mass[2]) - square(nu_mass[1]);
	delta_m32 = sqrt(square(square(nu_mass[3]) - square(nu_mass[2])));
	
	delta_m32_with_sign = square(nu_mass[3]) - square(nu_mass[2]);
	min_mass = min(nu_mass);
	Ue_squared = get_U_PMNS(nFamily(), sin2_th12, sin2_th13);
	
	m_beta_squared = get_effective_mass_squared(Ue_squared, nu_mass);
	if (m_beta_squared<0.){
		m_beta = -1.*pow(m_beta_squared, 0.5);
	}
	else{
		m_beta = pow(m_beta_squared, 0.5);
	}

	m_s = sum(nu_mass);

}


model{

	sin2_th12_means ~ normal(sin2_th12, sin2_th12_sigmas);
	sin2_th13_means ~ normal(sin2_th13, sin2_th13_sigmas);
	delta_m21_means ~ normal(delta_m21, delta_m21_sigmas);
	
	if (nu_mass[1] < nu_mass[3]){
	   delta_m32_means_NH ~ normal(delta_m32_with_sign, delta_m32_sigmas_NH);
	   sin2_th13_means_NH ~ normal(sin2_th13, sin2_th13_sigmas_NH);
	   }
	else if (nu_mass[3] < nu_mass[1]){
	   delta_m32_means_IH ~ normal(delta_m32_with_sign, delta_m32_sigmas_IH);
	   sin2_th13_means_IH ~ normal(sin2_th13, sin2_th13_sigmas_IH);
	   }

	if (use_m_beta == 1){ 
	   m_beta_squared_mean ~ normal(m_beta_squared, m_beta_squared_sigma);
	   }
        if (use_m_s == 1){
	   m_s_mean ~ normal(m_s, m_s_sigma);
	}
	
}