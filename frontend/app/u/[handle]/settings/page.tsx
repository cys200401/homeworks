import UserSettingsForm from "@/components/user/UserSettingsForm";

export default async function UserSettingsPage({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;

  return <UserSettingsForm handle={handle} />;
}
