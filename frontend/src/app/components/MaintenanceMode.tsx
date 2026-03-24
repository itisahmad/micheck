"use client";

import { useEffect, useState } from "react";

interface MaintenanceData {
  maintenance_mode: boolean;
  maintenance_message: string;
}

export default function MaintenanceMode() {
  const [maintenanceData, setMaintenanceData] = useState<MaintenanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkMaintenanceStatus = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/maintenance-status/`);
        const data = await response.json();
        setMaintenanceData(data);
        setLoading(false);
      } catch (error) {
        console.error("Failed to check maintenance status:", error);
        setLoading(false);
      }
    };

    checkMaintenanceStatus();
    
    // Check every 30 seconds
    const interval = setInterval(checkMaintenanceStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0c0f14] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#f59e0b] mx-auto mb-4"></div>
          <p className="text-[#6b7280]">Checking system status...</p>
        </div>
      </div>
    );
  }

  if (maintenanceData?.maintenance_mode) {
    return (
      <div className="min-h-screen bg-[#0c0f14] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-8">
            <div className="w-24 h-24 bg-[#f59e0b] rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="w-12 h-12 text-[#0c0f14]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c-.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
              </svg>
            </div>
          </div>
          
          <h1 className="font-display text-3xl font-bold text-white mb-4">
            Under Maintenance
          </h1>
          
          <div className="bg-[#1a1f2e] rounded-xl p-6 mb-6 border border-[#2a3142]">
            <p className="text-[#6b7280] text-lg leading-relaxed">
              {maintenanceData.maintenance_message}
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="bg-[#1a1f2e] rounded-lg p-4 border border-[#2a3142]">
              <h2 className="font-semibold text-white mb-2">What's happening?</h2>
              <p className="text-[#6b7280] text-sm">
                We're currently performing updates to improve your experience. This is temporary and we'll be back shortly.
              </p>
            </div>
            
            <div className="bg-[#1a1f2e] rounded-lg p-4 border border-[#2a3142]">
              <h2 className="font-semibold text-white mb-2">When will we be back?</h2>
              <p className="text-[#6b7280] text-sm">
                We expect to be back online soon. Thank you for your patience!
              </p>
            </div>
          </div>
          
          <div className="mt-8">
            <button
              onClick={() => window.location.reload()}
              className="bg-[#f59e0b] hover:bg-[#fbbf24] text-[#0c0f14] px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Check Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // If not in maintenance mode, don't render anything
  return null;
}
