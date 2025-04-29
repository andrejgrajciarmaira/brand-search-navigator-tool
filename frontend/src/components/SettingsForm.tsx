
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { format } from "date-fns";
import { CalendarIcon, Globe, Network, Languages, Clock, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useState } from "react";
import { SearchSettings } from "@/pages/Index";

const LOCATIONS = [
  { value: "United States", label: "United States" },
  { value: "United Kingdom", label: "United Kingdom" },
  { value: "Canada", label: "Canada" },
  { value: "Australia", label: "Australia" },
  { value: "Germany", label: "Germany" },
  { value: "France", label: "France" },
  { value: "Spain", label: "Spain" },
  { value: "Italy", label: "Italy" },
  { value: "Japan", label: "Japan" },
  { value: "India", label: "India" },
  { value: "Brazil", label: "Brazil" },
  { value: "Mexico", label: "Mexico" },
  { value: "Netherlands", label: "Netherlands" },
];

const LANGUAGES = [
  { value: "English", label: "English" },
  { value: "Spanish", label: "Spanish" },
  { value: "French", label: "French" },
  { value: "German", label: "German" },
  { value: "Italian", label: "Italian" },
  { value: "Portuguese", label: "Portuguese" },
  { value: "Japanese", label: "Japanese" },
  { value: "Chinese", label: "Chinese" },
  { value: "Russian", label: "Russian" },
  { value: "Arabic", label: "Arabic" },
  { value: "Hindi", label: "Hindi" },
  { value: "Dutch", label: "Dutch" },
];

interface SettingsFormProps {
  settings: SearchSettings;
  onChange: (settings: Partial<SearchSettings>) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const SettingsForm: React.FC<SettingsFormProps> = ({
  settings,
  onChange,
  onSubmit,
  isLoading
}) => {
  const [fromDate, setFromDate] = useState<Date | undefined>(
    settings.dateFrom ? new Date(settings.dateFrom) : undefined
  );
  
  const [toDate, setToDate] = useState<Date | undefined>(
    settings.dateTo ? new Date(settings.dateTo) : undefined
  );

  const handleFromDateSelect = (date: Date | undefined) => {
    setFromDate(date);
    if (date) {
      onChange({ dateFrom: format(date, "yyyy-MM-dd") });
    }
  };

  const handleToDateSelect = (date: Date | undefined) => {
    setToDate(date);
    if (date) {
      onChange({ dateTo: format(date, "yyyy-MM-dd") });
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-muted-foreground" />
          <Label className="font-medium">Location</Label>
        </div>
        <Select
          value={settings.location}
          onValueChange={(value) => onChange({ location: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select location" />
          </SelectTrigger>
          <SelectContent>
            {LOCATIONS.map((location) => (
              <SelectItem key={location.value} value={location.value}>
                {location.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Languages className="h-4 w-4 text-muted-foreground" />
          <Label className="font-medium">Language</Label>
        </div>
        <Select
          value={settings.language}
          onValueChange={(value) => onChange({ language: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select language" />
          </SelectTrigger>
          <SelectContent>
            {LANGUAGES.map((language) => (
              <SelectItem key={language.value} value={language.value}>
                {language.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-muted-foreground" />
          <Label className="font-medium">Network</Label>
        </div>
        <Select
          value={settings.network}
          onValueChange={(value: "google" | "google_search_partners" | "both") => 
            onChange({ network: value })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Select network" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="google">Google Search</SelectItem>
            <SelectItem value="google_search_partners">Google Search Partners</SelectItem>
            <SelectItem value="both">Both Networks</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <Label className="font-medium">Date Range</Label>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="fromDate" className="text-xs">From</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="fromDate"
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !fromDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {fromDate ? format(fromDate, "yyyy-MM-dd") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 pointer-events-auto">
                <Calendar
                  mode="single"
                  selected={fromDate}
                  onSelect={handleFromDateSelect}
                  initialFocus
                  disabled={(date) => date > new Date() || date < new Date('2015-01-01')}
                  className={cn("p-3 pointer-events-auto")}
                />
              </PopoverContent>
            </Popover>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="toDate" className="text-xs">To</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  id="toDate"
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !toDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {toDate ? format(toDate, "yyyy-MM-dd") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 pointer-events-auto">
                <Calendar
                  mode="single"
                  selected={toDate}
                  onSelect={handleToDateSelect}
                  initialFocus
                  disabled={(date) => date > new Date() || date < (fromDate || new Date('2015-01-01'))}
                  className={cn("p-3 pointer-events-auto")}
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <Label className="font-medium">Data Granularity</Label>
        <RadioGroup
          value={settings.granularity}
          onValueChange={(value: "monthly" | "quarterly" | "yearly") => 
            onChange({ granularity: value })
          }
          className="grid grid-cols-3 gap-4"
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="monthly" id="monthly" />
            <Label htmlFor="monthly">Monthly</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="quarterly" id="quarterly" />
            <Label htmlFor="quarterly">Quarterly</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="yearly" id="yearly" />
            <Label htmlFor="yearly">Yearly</Label>
          </div>
        </RadioGroup>
      </div>

      <Button 
        onClick={onSubmit} 
        className="w-full mt-6" 
        disabled={isLoading}
      >
        {isLoading ? "Generating Analysis..." : "Generate Share of Search Analysis"}
        {!isLoading && <ChevronRight className="ml-2 h-4 w-4" />}
      </Button>
    </div>
  );
};

export default SettingsForm;
