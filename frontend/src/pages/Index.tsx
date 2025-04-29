
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import BrandInputSection from "@/components/BrandInputSection";
import SettingsForm from "@/components/SettingsForm";
import ResultsSection from "@/components/ResultsSection";
import SetupGuide from "@/components/SetupGuide";
import { toast } from "sonner";
import { Search, BarChart3 } from "lucide-react";

// Define types for our data
export type Brand = {
  id: string;
  name: string;
  keywords: string[];
  isOwnBrand: boolean;
  color?: string;
};

export type SearchSettings = {
  location: string;
  language: string;
  network: "google" | "google_search_partners" | "both";
  dateFrom: string;
  dateTo: string;
  granularity: "monthly" | "quarterly" | "yearly";
};

export type SearchResult = {
  brand: string;
  period: string;
  volume: number;
  share: number;
  color: string;
};

// Pre-defined colors for brands visualization
const BRAND_COLORS = [
  '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
];

const Index = () => {
  const [step, setStep] = useState<'input' | 'results'>('input');
  const [brands, setBrands] = useState<Brand[]>([
    { id: '1', name: '', keywords: [''], isOwnBrand: true },
    { id: '2', name: '', keywords: [''], isOwnBrand: false }
  ]);
  const [searchSettings, setSearchSettings] = useState<SearchSettings>({
    location: 'United States',
    language: 'English',
    network: 'google',
    dateFrom: '2022-01-01',
    dateTo: new Date().toISOString().split('T')[0],
    granularity: 'monthly'
  });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleBrandChange = (updatedBrands: Brand[]) => {
    // Assign colors to brands that don't have them yet
    const newBrands = updatedBrands.map((brand, index) => {
      if (!brand.color) {
        return { ...brand, color: BRAND_COLORS[index % BRAND_COLORS.length] };
      }
      return brand;
    });
    
    setBrands(newBrands);
  };

  const handleSettingsChange = (settings: Partial<SearchSettings>) => {
    setSearchSettings(prev => ({ ...prev, ...settings }));
  };

  const validateForm = () => {
    // Check if at least one brand is defined with a name and keyword
    const hasBrands = brands.some(brand => brand.name && brand.keywords.some(k => k.trim() !== ''));
    
    if (!hasBrands) {
      toast.error("Please add at least one brand with keywords");
      return false;
    }

    // Check if dates are valid
    const fromDate = new Date(searchSettings.dateFrom);
    const toDate = new Date(searchSettings.dateTo);
    
    if (isNaN(fromDate.getTime()) || isNaN(toDate.getTime())) {
      toast.error("Please enter valid dates");
      return false;
    }

    if (fromDate > toDate) {
      toast.error("Start date must be before end date");
      return false;
    }

    return true;
  };

  const handlePrepareAnalysis = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    
    // In a real app, we would make an API call here to fetch data from Google Ads
    // For now, we'll simulate the API call with a timeout and mock data
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create mock data based on the brands and time range
      const mockResults = generateMockResults(brands, searchSettings);
      setResults(mockResults);
      setStep('results');
    } catch (error) {
      console.error("Error generating analysis:", error);
      toast.error("Failed to generate analysis. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockResults = (brands: Brand[], settings: SearchSettings): SearchResult[] => {
    const results: SearchResult[] = [];
    const startYear = parseInt(settings.dateFrom.split('-')[0]);
    const endYear = parseInt(settings.dateTo.split('-')[0]);
    
    for (let year = startYear; year <= endYear; year++) {
      // Base volume that increases for each brand over the years
      const baseVolume = 1000 + (year - startYear) * 200;
      
      for (const brand of brands) {
        if (!brand.name || brand.keywords.every(k => k.trim() === '')) continue;
        
        // Calculate volume based on number of keywords and a random factor
        let volume = baseVolume * (brand.keywords.filter(k => k.trim() !== '').length);
        // Add randomness (±30%)
        volume *= (0.7 + Math.random() * 0.6);
        
        results.push({
          brand: brand.name,
          period: year.toString(),
          volume: Math.round(volume),
          share: 0, // Will calculate shares after all volumes are set
          color: brand.color || '#cccccc'
        });
      }
    }
    
    // Calculate share percentages for each period
    const periods = [...new Set(results.map(r => r.period))];
    
    periods.forEach(period => {
      const periodResults = results.filter(r => r.period === period);
      const totalVolume = periodResults.reduce((sum, r) => sum + r.volume, 0);
      
      periodResults.forEach(result => {
        const resultIndex = results.findIndex(r => r.period === period && r.brand === result.brand);
        if (resultIndex >= 0) {
          results[resultIndex].share = totalVolume ? parseFloat((result.volume / totalVolume * 100).toFixed(1)) : 0;
        }
      });
    });
    
    return results;
  };

  const resetAnalysis = () => {
    setStep('input');
    setResults([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-10 w-10 text-brandblue" />
            <h1 className="text-3xl font-bold text-gray-900">Share of Search Tool</h1>
          </div>
          <SetupGuide />
        </div>
        
        {step === 'input' ? (
          <>
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-4">
                  <Search className="h-5 w-5 text-muted-foreground" />
                  <h2 className="text-xl font-semibold">Search Parameters</h2>
                </div>
                
                <div className="grid gap-8 md:grid-cols-2">
                  <BrandInputSection brands={brands} onChange={handleBrandChange} />
                  <SettingsForm 
                    settings={searchSettings} 
                    onChange={handleSettingsChange}
                    onSubmit={handlePrepareAnalysis}
                    isLoading={isLoading}
                  />
                </div>
              </CardContent>
            </Card>
            
            <div className="text-sm text-gray-500 p-4 bg-infoblue rounded-lg mb-6">
              <p className="font-medium mb-1">Note:</p>
              <p>Google Ads API returns data only for available periods (typically max. 4-5 years back), depending on when you select the "From date".</p>
            </div>
          </>
        ) : (
          <ResultsSection 
            results={results} 
            settings={searchSettings}
            brands={brands}
            onReset={resetAnalysis} 
          />
        )}
      </div>
    </div>
  );
};

export default Index;
