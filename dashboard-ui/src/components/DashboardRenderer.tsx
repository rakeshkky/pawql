import React, { useEffect, useRef } from 'react';
import { DashboardData } from '../types';

interface DashboardRendererProps {
  dashboardData: DashboardData;
}

export const DashboardRenderer: React.FC<DashboardRendererProps> = ({
  dashboardData
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current && dashboardData.dashboard_html) {
      const iframe = iframeRef.current;
      const doc = iframe.contentDocument || iframe.contentWindow?.document;
      
      if (doc) {
        doc.open();
        doc.write(dashboardData.dashboard_html);
        doc.close();
      }
    }
  }, [dashboardData.dashboard_html]);

  return (
    <div className="card animate-fade-in">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-gray-800">
          {dashboardData.location_name} Dashboard
        </h2>
        <span className="text-sm text-gray-500">
          {new Date(dashboardData.date).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </span>
      </div>
      
      <div className="relative">
        <iframe
          ref={iframeRef}
          className="w-full h-screen border-0 rounded-lg"
          title="Dashboard"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  );
};
