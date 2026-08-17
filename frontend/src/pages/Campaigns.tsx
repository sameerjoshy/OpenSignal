import { Link } from "react-router-dom";
import { useCampaigns } from "../hooks/useCampaigns";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { StatusBadge } from "../components/Badges";
import { formatDate, formatNumber } from "../utils/format";

export default function Campaigns() {
  const { campaigns, loading, error } = useCampaigns();

  return (
    <div className="stack">
      <div className="filter-bar">
        <div className="filter-spacer" />
        <Link to="/campaigns/new" className="btn btn-primary">
          + New campaign
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="page-loading">
          <Spinner />
        </div>
      ) : campaigns.length === 0 ? (
        <EmptyState
          title="No campaigns yet"
          description="Create a campaign to import target companies and generate personalized outreach."
          action={
            <Link to="/campaigns/new" className="btn btn-primary">
              Create campaign
            </Link>
          }
        />
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Status</th>
                <th>Accounts</th>
                <th>Sent</th>
                <th>Replies</th>
                <th>Created</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td>
                    <div className="cell-title">{campaign.name}</div>
                    {campaign.description && <div className="cell-sub">{campaign.description}</div>}
                  </td>
                  <td>
                    <StatusBadge status={campaign.status} />
                  </td>
                  <td>{campaign.account_count ?? "—"}</td>
                  <td>{formatNumber(campaign.sent_count ?? 0)}</td>
                  <td>{formatNumber(campaign.reply_count ?? 0)}</td>
                  <td className="cell-time">{formatDate(campaign.created_at)}</td>
                  <td>
                    <Link to={`/campaigns/${campaign.id}`} className="btn btn-secondary btn-sm">
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}