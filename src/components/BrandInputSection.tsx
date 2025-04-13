
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, X, Building, Users } from "lucide-react";
import { Brand } from "@/pages/Index";

interface BrandInputSectionProps {
  brands: Brand[];
  onChange: (brands: Brand[]) => void;
}

const BrandInputSection: React.FC<BrandInputSectionProps> = ({ brands, onChange }) => {
  const [activeTab, setActiveTab] = useState<"own" | "competitors">("own");

  const ownBrands = brands.filter(brand => brand.isOwnBrand);
  const competitorBrands = brands.filter(brand => !brand.isOwnBrand);

  const handleBrandNameChange = (id: string, value: string) => {
    const updatedBrands = brands.map(brand => 
      brand.id === id ? { ...brand, name: value } : brand
    );
    onChange(updatedBrands);
  };

  const handleKeywordChange = (brandId: string, index: number, value: string) => {
    const updatedBrands = brands.map(brand => {
      if (brand.id === brandId) {
        const keywords = [...brand.keywords];
        keywords[index] = value;
        return { ...brand, keywords };
      }
      return brand;
    });
    onChange(updatedBrands);
  };

  const addKeyword = (brandId: string) => {
    const updatedBrands = brands.map(brand => {
      if (brand.id === brandId) {
        return { ...brand, keywords: [...brand.keywords, ''] };
      }
      return brand;
    });
    onChange(updatedBrands);
  };

  const removeKeyword = (brandId: string, index: number) => {
    const updatedBrands = brands.map(brand => {
      if (brand.id === brandId) {
        const keywords = [...brand.keywords];
        keywords.splice(index, 1);
        return { ...brand, keywords: keywords.length ? keywords : [''] };
      }
      return brand;
    });
    onChange(updatedBrands);
  };

  const addBrand = (isOwnBrand: boolean) => {
    const newBrand: Brand = {
      id: Date.now().toString(),
      name: '',
      keywords: [''],
      isOwnBrand
    };
    onChange([...brands, newBrand]);
  };

  const removeBrand = (id: string) => {
    const updatedBrands = brands.filter(brand => brand.id !== id);
    onChange(updatedBrands);
  };

  const renderBrandInputs = (brandList: Brand[]) => {
    if (brandList.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4">No brands added yet</p>
          <Button 
            onClick={() => addBrand(activeTab === "own")}
            variant="outline"
            className="flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add {activeTab === "own" ? "Own Brand" : "Competitor"}
          </Button>
        </div>
      );
    }

    return brandList.map(brand => (
      <div key={brand.id} className="mb-6 border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <Label htmlFor={`brand-${brand.id}`} className="font-semibold">
            Brand Name
          </Label>
          {brandList.length > 1 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeBrand(brand.id)}
              className="h-8 w-8 text-muted-foreground hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        
        <Input
          id={`brand-${brand.id}`}
          value={brand.name}
          onChange={(e) => handleBrandNameChange(brand.id, e.target.value)}
          placeholder="Enter brand name"
          className="mb-4"
        />
        
        <div className="space-y-2">
          <Label className="font-semibold">Related Keywords</Label>
          {brand.keywords.map((keyword, index) => (
            <div key={`${brand.id}-kw-${index}`} className="flex gap-2">
              <Input
                value={keyword}
                onChange={(e) => handleKeywordChange(brand.id, index, e.target.value)}
                placeholder={`Keyword ${index + 1}`}
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeKeyword(brand.id, index)}
                disabled={brand.keywords.length <= 1}
                className="h-10 w-10 flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            variant="outline"
            className="mt-2 w-full"
            onClick={() => addKeyword(brand.id)}
            size="sm"
          >
            <Plus className="h-4 w-4 mr-2" /> Add Keyword
          </Button>
        </div>
      </div>
    ));
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Brand Keywords</h3>
      
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "own" | "competitors")}>
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="own" className="flex items-center">
            <Building className="h-4 w-4 mr-2" />
            My Brand
          </TabsTrigger>
          <TabsTrigger value="competitors" className="flex items-center">
            <Users className="h-4 w-4 mr-2" />
            Competitors
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="own" className="border-0 p-0">
          {renderBrandInputs(ownBrands)}
          {ownBrands.length > 0 && (
            <Button
              variant="outline"
              className="mt-2 w-full"
              onClick={() => addBrand(true)}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" /> Add Another Brand
            </Button>
          )}
        </TabsContent>
        
        <TabsContent value="competitors" className="border-0 p-0">
          {renderBrandInputs(competitorBrands)}
          {competitorBrands.length > 0 && (
            <Button
              variant="outline"
              className="mt-2 w-full"
              onClick={() => addBrand(false)}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" /> Add Another Competitor
            </Button>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BrandInputSection;
