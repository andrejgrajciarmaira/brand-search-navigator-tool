
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Download, ArrowLeft, PieChart, BarChart3, Table2 } from "lucide-react";
import { Brand, SearchResult, SearchSettings } from "@/pages/Index";

interface ResultsSectionProps {
  results: SearchResult[];
  settings: SearchSettings;
  brands: Brand[];
  onReset: () => void;
}

interface GroupedResult {
  period: string;
  [key: string]: string | number;
  total?: number;
}

const ResultsSection: React.FC<ResultsSectionProps> = ({ results, settings, brands, onReset }) => {
  const [activeTab, setActiveTab] = useState("share");

  // Group results by period for easier chart rendering
  const groupedResults = results.reduce<GroupedResult[]>((acc, result) => {
    let periodData = acc.find(item => item.period === result.period);
    
    if (!periodData) {
      periodData = { period: result.period };
      acc.push(periodData);
    }
    
    periodData[result.brand] = result.volume;
    
    return acc;
  }, []);

  // Calculate totals for each period
  groupedResults.forEach(period => {
    let total = 0;
    for (const brand of brands) {
      if (period[brand.name]) {
        total += Number(period[brand.name]);
      }
    }
    period.total = total;
  });

  // Stack data for percentage chart
  const stackedData = groupedResults.map(period => {
    const result: GroupedResult = { period: period.period };
    
    brands
      .filter(b => b.name) // Only include brands that have names
      .forEach(brand => {
        if (period[brand.name]) {
          const volume = Number(period[brand.name]);
          const percentage = period.total ? (volume / period.total * 100) : 0;
          result[`${brand.name}`] = parseFloat(percentage.toFixed(1));
        }
      });
    
    return result;
  });

  // Create a color map for the brands
  const brandColors = brands
    .filter(b => b.name)
    .reduce<Record<string, string>>((acc, brand) => {
      acc[brand.name] = brand.color || "#cccccc";
      return acc;
    }, {});

  const handleDownloadChart = (chartType: string) => {
    // Implementation would connect to actual download functionality
    console.log(`Downloading ${chartType} chart`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={onReset}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Parameters
          </Button>
          <h2 className="text-xl font-semibold">
            {settings.granularity === "yearly" ? "Yearly" : 
             settings.granularity === "quarterly" ? "Quarterly" : "Monthly"} Report | 
            {" "}Location: {settings.location}, Language: {settings.language}
          </h2>
        </div>
      </div>
      
      <Tabs 
        defaultValue="share" 
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
      >
        <TabsList className="grid grid-cols-3 w-full max-w-md mx-auto mb-6">
          <TabsTrigger value="share" className="flex items-center">
            <PieChart className="h-4 w-4 mr-2" />
            Share %
          </TabsTrigger>
          <TabsTrigger value="volume" className="flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Volume
          </TabsTrigger>
          <TabsTrigger value="data" className="flex items-center">
            <Table2 className="h-4 w-4 mr-2" />
            Raw Data
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="share" className="mt-0">
          <Card>
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Share of Search (%)</h3>
                <Button variant="outline" size="sm" onClick={() => handleDownloadChart("share")}>
                  <Download className="h-4 w-4 mr-2" /> Download Chart
                </Button>
              </div>
              
              <div className="h-[500px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={stackedData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
                    stackOffset="expand"
                    barGap={0}
                    barCategoryGap={30}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis tickFormatter={(value) => `${value}%`} />
                    <Tooltip formatter={(value) => [`${value}%`, ""]} />
                    <Legend />
                    {brands
                      .filter(brand => brand.name)
                      .map(brand => (
                        <Bar
                          key={brand.name}
                          dataKey={brand.name}
                          stackId="a"
                          fill={brand.color}
                          name={brand.name}
                        />
                      ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="volume" className="mt-0">
          <Card>
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Search Volume (Absolute)</h3>
                <Button variant="outline" size="sm" onClick={() => handleDownloadChart("volume")}>
                  <Download className="h-4 w-4 mr-2" /> Download Chart
                </Button>
              </div>
              
              <div className="h-[500px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={groupedResults}
                    margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {brands
                      .filter(brand => brand.name)
                      .map(brand => (
                        <Bar
                          key={brand.name}
                          dataKey={brand.name}
                          fill={brand.color}
                          name={brand.name}
                        />
                      ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="data" className="mt-0">
          <Card>
            <CardContent className="pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Raw Data</h3>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" /> Export to CSV
                </Button>
              </div>
              
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Period</TableHead>
                      <TableHead>Brand</TableHead>
                      <TableHead className="text-right">Volume</TableHead>
                      <TableHead className="text-right">Share %</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {results.map((result, i) => (
                      <TableRow key={`${result.brand}-${result.period}-${i}`}>
                        <TableCell>{result.period}</TableCell>
                        <TableCell className="flex items-center">
                          <div 
                            className="w-3 h-3 rounded-full mr-2"
                            style={{ backgroundColor: result.color }}
                          ></div>
                          {result.brand}
                        </TableCell>
                        <TableCell className="text-right">{result.volume.toLocaleString()}</TableCell>
                        <TableCell className="text-right">{result.share.toFixed(1)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ResultsSection;
