import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { HelpCircle } from "lucide-react";

const SetupGuide = () => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <HelpCircle className="h-4 w-4" />
          Setup Guide
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Google Ads API Setup Guide</DialogTitle>
          <DialogDescription>
            Follow these steps to set up the Google Ads API for your Share of Search Tool.
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 space-y-4">
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="prereq">
              <AccordionTrigger>Prerequisites</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <p>Before you start, make sure you have:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>A Google Ads account with admin access</li>
                  <li>A Google Cloud Platform account</li>
                  <li>Node.js (version 14+) installed on your machine</li>
                  <li>Git installed on your machine</li>
                </ul>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step1">
              <AccordionTrigger>Step 1: Set up a Google Cloud Project</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>Go to the <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Cloud Console</a></p>
                  </li>
                  <li>
                    <p>Create a new project or select an existing one</p>
                  </li>
                  <li>
                    <p>From the navigation menu, select "APIs & Services" &gt; "Library"</p>
                  </li>
                  <li>
                    <p>Search for "Google Ads API" and enable it for your project</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step2">
              <AccordionTrigger>Step 2: Create OAuth 2.0 Credentials</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>In the Google Cloud Console, go to "APIs & Services" &gt; "Credentials"</p>
                  </li>
                  <li>
                    <p>Click "Create Credentials" and select "OAuth client ID"</p>
                  </li>
                  <li>
                    <p>Select "Web application" as the application type</p>
                  </li>
                  <li>
                    <p>Add a name for your OAuth client</p>
                  </li>
                  <li>
                    <p>Add "http://localhost:8080/callback" as an authorized redirect URI</p>
                  </li>
                  <li>
                    <p>Click "Create" and save your Client ID and Client Secret</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step3">
              <AccordionTrigger>Step 3: Create Developer Token</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>Log in to your Google Ads account at <a href="https://ads.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">ads.google.com</a></p>
                  </li>
                  <li>
                    <p>Click on the tools icon in the upper right corner</p>
                  </li>
                  <li>
                    <p>Under "Setup", select "API Center"</p>
                  </li>
                  <li>
                    <p>Apply for a developer token by filling out the required information</p>
                    <p className="text-sm text-muted-foreground mt-1">Note: For testing purposes, you can use a test account which provides immediate access with limited functionality</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step4">
              <AccordionTrigger>Step 4: Clone and Configure the Project</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>Clone the project repository:</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
                      git clone https://github.com/yourusername/share-of-search-tool.git
                      cd share-of-search-tool
                    </pre>
                  </li>
                  <li>
                    <p>Install dependencies:</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
                      npm install
                    </pre>
                  </li>
                  <li>
                    <p>Create a <code>.env</code> file in the project root with the following content (you can copy from <code>.env.example</code>):</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
{`# Google Ads API credentials
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_DEVELOPER_TOKEN=your-developer-token
GOOGLE_LOGIN_CUSTOMER_ID=your-manager-id (optional)
GOOGLE_REFRESH_TOKEN=your-refresh-token (will be obtained during authentication)`}
                    </pre>
                    <p className="text-sm text-muted-foreground mt-1">Replace the placeholders with your actual credentials</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step5">
              <AccordionTrigger>Step 5: Obtain a Refresh Token</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>Install required dependencies for the authentication script:</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
                      npm install google-auth-library dotenv open
                    </pre>
                  </li>
                  <li>
                    <p>Run the authentication script directly:</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
                      node scripts/auth.js
                    </pre>
                  </li>
                  <li>
                    <p>Follow the prompts to authorize the application in your browser</p>
                  </li>
                  <li>
                    <p>After successful authorization, the refresh token will be saved in your <code>.env</code> file automatically</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="step6">
              <AccordionTrigger>Step 6: Run the Application</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <ol className="list-decimal pl-6 space-y-4">
                  <li>
                    <p>Start the development server:</p>
                    <pre className="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm my-2">
                      npm run dev
                    </pre>
                  </li>
                  <li>
                    <p>Open your browser and navigate to <code>http://localhost:8080</code></p>
                  </li>
                  <li>
                    <p>You should now be able to use the Share of Search Tool with real Google Ads data!</p>
                  </li>
                </ol>
              </AccordionContent>
            </AccordionItem>
            
            <AccordionItem value="troubleshooting">
              <AccordionTrigger>Troubleshooting</AccordionTrigger>
              <AccordionContent className="space-y-2">
                <p className="font-medium">Common Issues:</p>
                
                <div className="space-y-4 mt-2">
                  <div>
                    <p className="font-medium text-sm">Authentication Failed</p>
                    <p className="text-sm">Ensure your client ID, client secret, and developer token are correct. Double-check your redirect URI in the Google Cloud Console.</p>
                  </div>
                  
                  <div>
                    <p className="font-medium text-sm">API Quota Exceeded</p>
                    <p className="text-sm">Google Ads API has usage quotas. If you exceed them, you'll need to wait or request a quota increase.</p>
                  </div>
                  
                  <div>
                    <p className="font-medium text-sm">No Data Being Retrieved</p>
                    <p className="text-sm">Ensure that your Google Ads account has active campaigns and that you're using the correct customer ID.</p>
                  </div>
                  
                  <div>
                    <p className="font-medium text-sm">For additional help:</p>
                    <ul className="list-disc pl-6 space-y-1 text-sm">
                      <li>Check the <a href="https://developers.google.com/google-ads/api/docs/start" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Ads API Documentation</a></li>
                      <li>Join the <a href="https://groups.google.com/g/adwords-api" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Ads API Forum</a></li>
                    </ul>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SetupGuide;
