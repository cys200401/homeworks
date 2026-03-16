import UserWorkspace from "@/components/user/UserWorkspace";

export default async function UserWorkspacePage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;

  return <UserWorkspace handle={handle} />;
}
