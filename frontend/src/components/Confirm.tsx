import Modal from "./Modal";

export interface ConfirmState {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
}

export default function ConfirmDialog({ state, onClose }: { state: ConfirmState | null; onClose: () => void }) {
  if (!state) return null;
  return (
    <Modal
      open
      title={state.title}
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button
            className={`btn ${state.danger ? "btn-danger" : "btn-primary"}`}
            onClick={() => {
              onClose();
              state.onConfirm();
            }}
          >
            {state.confirmLabel || "Confirm"}
          </button>
        </>
      }
    >
      <p className="muted" style={{ margin: 0 }}>
        {state.message}
      </p>
    </Modal>
  );
}