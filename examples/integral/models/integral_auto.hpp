template <typename T>
typename boost::math::tools::promote_args<T>::type
calculate_integral(const T& threshold, std::ostream* pstream) {
	/* Read the spectrum and normalize. */
	TFile* file = new TFile("integral/models/model_input/spectrum.root", "READ");
	TH1D* spectrum = (TH1D*)file->Get("th");
	spectrum->Scale(1/spectrum->Integral());
	int low = spectrum->FindBin(threshold);
	int up = spectrum->GetNbinsX();
	double integral = spectrum->Integral(low, up);
	delete spectrum;
	file->Close();
	delete file;
	return integral;
}

