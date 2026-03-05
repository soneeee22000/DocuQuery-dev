"use client";

/**
 * Dashboard home page with stats, quick actions, and recent activity.
 */

import Link from "next/link";
import { FileText, PlusCircle, BarChart3 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { useDashboardStats } from "@/hooks/use-dashboard";
import { formatDate, getScoreVariant } from "@/lib/score-utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const { stats, isLoading } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const isNewUser =
    stats &&
    stats.resumeCount === 0 &&
    stats.jdCount === 0 &&
    stats.analysisCount === 0;

  if (isNewUser) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold">
          Welcome, {user?.email?.split("@")[0]}
        </h2>
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
            <p className="text-lg font-medium">Get started with DocuQuery</p>
            <p className="text-muted-foreground">
              Upload your resume and a job description to receive a match
              analysis with actionable tips.
            </p>
            <Button asChild>
              <Link href="/documents">Upload Your First Document</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>

      {/* Stat cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Resumes</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.resumeCount ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Job Descriptions
            </CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.jdCount ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Analyses</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.analysisCount ?? 0}</p>
            {stats && stats.analysisCount > 0 && (
              <p className="text-xs text-muted-foreground">
                Avg score: {stats.averageScore}/100
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="transition-colors hover:bg-accent/50">
          <Link href="/documents">
            <CardContent className="flex items-center gap-4 py-6">
              <FileText className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">Upload Document</p>
                <p className="text-sm text-muted-foreground">
                  Add a resume or job description
                </p>
              </div>
            </CardContent>
          </Link>
        </Card>
        <Card className="transition-colors hover:bg-accent/50">
          <Link href="/analysis/new">
            <CardContent className="flex items-center gap-4 py-6">
              <PlusCircle className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium">New Analysis</p>
                <p className="text-sm text-muted-foreground">
                  Match your resume against a job posting
                </p>
              </div>
            </CardContent>
          </Link>
        </Card>
      </div>

      {/* Recent activity */}
      {stats && stats.recentAnalyses.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Recent Analyses</h3>
            <Button asChild variant="ghost" size="sm">
              <Link href="/analysis">View All</Link>
            </Button>
          </div>
          {stats.recentAnalyses.map((a) => (
            <Card key={a.id}>
              <CardContent className="flex items-center justify-between py-3">
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {a.resume_name} &rarr; {a.jd_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(a.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={getScoreVariant(a.score)}>
                    {a.score}/100
                  </Badge>
                  <Button asChild variant="outline" size="sm">
                    <Link href={`/analysis/${a.id}`}>View</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
