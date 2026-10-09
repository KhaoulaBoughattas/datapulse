"use client";

import { ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

export default function RoleGate({ permission, children }: { permission: string; children: ReactNode }) {
  const { can } = useAuth();
  if (!can(permission)) return null;
  return <>{children}</>;
}
