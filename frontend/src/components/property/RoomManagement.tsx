"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { AnimatePresence, motion } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  Check,
  MoreHorizontal,
  Pencil,
  Plus,
  SlidersHorizontal,
  Trash2,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { devicesApi, propertiesApi, roomsApi } from "@/lib/api";
import type { Room, SavedDevice } from "@/lib/types";
import { cn } from "@/lib/utils";

// ── Vendor badge ──────────────────────────────────────────────────────────────

const VENDOR_COLOURS: Record<string, string> = {
  shelly: "bg-amber-bg text-amber border-amber/20",
  govee: "bg-surface-2 text-text-2 border-border",
  lifx: "bg-surface-2 text-text-2 border-border",
  matter: "bg-green-bg text-green border-green/20",
  demo: "bg-surface-2 text-text-3 border-border",
};

function VendorBadge({ vendor }: { vendor: string }) {
  const cls = VENDOR_COLOURS[vendor.toLowerCase()] ?? "bg-surface-2 text-text-3 border-border";
  return (
    <span className={`inline-flex items-center font-mono text-xs px-2 py-0.5 rounded-full capitalize border ${cls}`}>
      {vendor}
    </span>
  );
}

// ── Saved device card ─────────────────────────────────────────────────────────

function SavedDeviceCard({
  device,
  propertyId,
  isDragging = false,
}: {
  device: SavedDevice;
  propertyId: string;
  isDragging?: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(device.name);
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const router = useRouter();

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  const renameMut = useMutation({
    mutationFn: (name: string) =>
      fetch(`/api/v1/integrations/devices/${device.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      }).then((r) => {
        if (!r.ok) throw new Error("rename failed");
        return r.json();
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-devices", propertyId] });
      setEditing(false);
    },
    onError: () => setEditing(false),
  });

  function commitRename() {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== device.name) renameMut.mutate(trimmed);
    else { setDraft(device.name); setEditing(false); }
  }

  const cardHref = `/properties/${propertyId}/devices/${device.id}`;

  return (
    <div
      onClick={(e) => {
        if (editing || isDragging) return;
        if ((e.target as HTMLElement).closest("button, a")) return;
        router.push(cardHref);
      }}
      className={cn(
        "bg-surface border border-border rounded-xl px-4 py-3 space-y-2 transition-all duration-150 select-none",
        isDragging
          ? "border-border-strong shadow-sm"
          : "cursor-pointer hover:border-border-strong hover:bg-surface-2",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        {editing ? (
          <div
            className="flex items-center gap-1.5 flex-1 min-w-0"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitRename();
                if (e.key === "Escape") { setDraft(device.name); setEditing(false); }
              }}
              className="flex-1 min-w-0 bg-surface-2 border border-border-strong rounded px-2 py-0.5 text-sm text-text font-body focus:outline-none"
            />
            <button
              onClick={commitRename}
              disabled={renameMut.isPending}
              className="text-green shrink-0"
            >
              <Check size={13} />
            </button>
            <button
              onClick={() => { setDraft(device.name); setEditing(false); }}
              className="text-text-3 shrink-0"
            >
              <X size={13} />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 min-w-0 flex-1">
            <Link
              href={cardHref}
              className="font-body text-sm text-text leading-snug truncate hover:text-text-2 transition-colors"
              onClick={(e) => isDragging && e.preventDefault()}
            >
              {draft}
            </Link>
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setEditing(true); }}
              className="text-text-3 hover:text-text-2 shrink-0 transition-colors"
            >
              <Pencil size={11} />
            </button>
          </div>
        )}
        <span className="flex items-center gap-1 font-mono text-xs text-text-3 shrink-0 mt-0.5">
          {device.vendor === "demo" ? (
            <Wifi size={7} className="text-green" />
          ) : (
            <WifiOff size={7} />
          )}
          {device.vendor === "demo" ? "Online" : "Saved"}
        </span>
      </div>
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <VendorBadge vendor={device.vendor} />
          {device.model && (
            <span className="font-body font-light text-xs text-text-3">{device.model}</span>
          )}
        </div>
        <SlidersHorizontal size={11} className="text-text-3 shrink-0" />
      </div>
    </div>
  );
}

// ── Draggable device card ─────────────────────────────────────────────────────

function DraggableCard({ device, propertyId }: { device: SavedDevice; propertyId: string }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: device.id,
    data: { device },
  });

  const style: React.CSSProperties = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="touch-none cursor-grab active:cursor-grabbing"
    >
      <SavedDeviceCard device={device} propertyId={propertyId} />
    </div>
  );
}

// ── Room section (droppable) ──────────────────────────────────────────────────

function RoomSection({
  room,
  devices,
  propertyId,
  onDeleteRequest,
  onRoomRenamed,
}: {
  room: Room;
  devices: SavedDevice[];
  propertyId: string;
  onDeleteRequest: (room: Room) => void;
  onRoomRenamed: (roomId: string, name: string) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: room.id });
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(room.name);
  const [menuOpen, setMenuOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  function commitRename() {
    const name = draft.trim();
    if (!name) { setDraft(room.name); setEditing(false); return; }
    if (name !== room.name) onRoomRenamed(room.id, name);
    setEditing(false);
  }

  return (
    <div className="space-y-3">
      {/* Room header */}
      <div className="flex items-center gap-3">
        {editing ? (
          <div className="flex items-center gap-1.5 flex-1">
            <input
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitRename();
                if (e.key === "Escape") { setDraft(room.name); setEditing(false); }
              }}
              onBlur={commitRename}
              className="bg-surface-2 border border-border-strong rounded px-2 py-0.5 text-xs font-body text-text focus:outline-none uppercase tracking-widest"
            />
          </div>
        ) : (
          <h3 className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
            {room.name}
            {room.floor != null && (
              <span className="ml-2 normal-case font-light">· Floor {room.floor}</span>
            )}
          </h3>
        )}
        <div className="flex-1 border-t border-border" />
        <span className="font-mono text-xs text-text-3">{devices.length}</span>

        {/* Room menu */}
        <div className="relative">
          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="text-text-3 hover:text-text-2 transition-colors p-0.5"
          >
            <MoreHorizontal size={13} />
          </button>
          <AnimatePresence>
            {menuOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.1 }}
                  className="absolute right-0 top-6 z-20 bg-surface border border-border rounded-xl shadow-sm py-1 min-w-[140px]"
                >
                  <button
                    onClick={() => { setMenuOpen(false); setEditing(true); }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs font-body text-text hover:bg-surface-2 transition-colors"
                  >
                    <Pencil size={12} /> Rename
                  </button>
                  <button
                    onClick={() => { setMenuOpen(false); onDeleteRequest(room); }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs font-body text-red hover:bg-red-bg transition-colors"
                  >
                    <Trash2 size={12} /> Delete room
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Droppable zone */}
      <div
        ref={setNodeRef}
        className={cn(
          "min-h-20 rounded-xl transition-all duration-150",
          isOver && "bg-surface-2/60 ring-2 ring-graphite/20",
          devices.length === 0 && !isOver &&
            "border-2 border-dashed border-border flex items-center justify-center py-6",
        )}
      >
        {devices.length === 0 ? (
          <p className="font-body font-light text-xs text-text-3 text-center">
            {isOver ? "Drop here" : "Drag devices here or add a new device"}
          </p>
        ) : (
          <motion.div layout className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {devices.map((d) => (
              <motion.div key={d.id} layout>
                <DraggableCard device={d} propertyId={propertyId} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}

// ── Unassigned section (droppable) ────────────────────────────────────────────

function UnassignedSection({
  devices,
  propertyId,
}: {
  devices: SavedDevice[];
  propertyId: string;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: "__unassigned__" });

  if (devices.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <h3 className="font-body font-normal text-xs uppercase tracking-widest text-text-3">
          Unassigned
        </h3>
        <div className="flex-1 border-t border-border" />
        <span className="font-mono text-xs text-text-3">{devices.length}</span>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          "min-h-20 rounded-xl transition-all duration-150",
          isOver && "bg-surface-2/60 ring-2 ring-graphite/20",
        )}
      >
        <motion.div layout className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {devices.map((d) => (
            <motion.div key={d.id} layout>
              <DraggableCard device={d} propertyId={propertyId} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}

// ── Delete room dialog ────────────────────────────────────────────────────────

function DeleteRoomDialog({
  room,
  deviceCount,
  onConfirm,
  onCancel,
  isPending,
}: {
  room: Room;
  deviceCount: number;
  onConfirm: () => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-graphite/40 backdrop-blur-sm" onClick={onCancel} />
      <motion.div
        className="relative bg-surface border border-border rounded-2xl p-6 max-w-sm w-full shadow-sm"
        initial={{ scale: 0.95, y: 8 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 8 }}
      >
        <h3 className="font-body font-normal text-base text-text mb-2">Delete {room.name}?</h3>
        <p className="font-body font-light text-sm text-text-2 mb-6">
          {deviceCount > 0 ? (
            <>
              <span className="font-mono">{deviceCount}</span>{" "}
              device{deviceCount !== 1 ? "s" : ""} will be moved to{" "}
              <span className="text-text">Unassigned</span>. The room will be permanently deleted.
            </>
          ) : (
            "This empty room will be permanently deleted."
          )}
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 bg-surface-2 text-text font-body text-sm rounded-lg px-4 py-2.5 hover:bg-border transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isPending}
            className="flex-1 bg-red text-surface font-body text-sm rounded-lg px-4 py-2.5 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {isPending ? "Deleting…" : "Delete room"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Delete property dialog ────────────────────────────────────────────────────

function DeletePropertyDialog({
  propertyName,
  roomCount,
  deviceCount,
  onConfirm,
  onCancel,
  isPending,
}: {
  propertyName: string;
  roomCount: number;
  deviceCount: number;
  onConfirm: () => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const [input, setInput] = useState("");
  const matches = input.trim() === propertyName.trim();

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-graphite/40 backdrop-blur-sm" onClick={onCancel} />
      <motion.div
        className="relative bg-surface border border-border rounded-2xl p-6 max-w-md w-full shadow-sm"
        initial={{ scale: 0.95, y: 8 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 8 }}
      >
        <h3 className="font-body font-normal text-base text-text mb-2">Delete property?</h3>
        <p className="font-body font-light text-sm text-text-2 mb-4">
          This will permanently remove{" "}
          <span className="font-mono text-text">{roomCount}</span> room{roomCount !== 1 ? "s" : ""}{" "}
          and{" "}
          <span className="font-mono text-text">{deviceCount}</span> device{deviceCount !== 1 ? "s" : ""}.{" "}
          <span className="text-red">This cannot be undone.</span>
        </p>
        <p className="font-body font-light text-xs text-text-3 mb-2">
          Type <span className="font-mono text-text">{propertyName}</span> to confirm:
        </p>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={propertyName}
          className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2 text-sm font-body text-text focus:outline-none focus:border-border-strong mb-4"
        />
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 bg-surface-2 text-text font-body text-sm rounded-lg px-4 py-2.5 hover:bg-border transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={!matches || isPending}
            className="flex-1 bg-red text-surface font-body text-sm rounded-lg px-4 py-2.5 hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            {isPending ? "Deleting…" : "Delete property"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Main RoomManagement component ─────────────────────────────────────────────

interface Props {
  propertyId: string;
  propertyName: string;
  rooms: Room[];
  savedDevices: SavedDevice[];
}

export function RoomManagement({ propertyId, propertyName, rooms, savedDevices }: Props) {
  const router = useRouter();
  const queryClient = useQueryClient();

  // DnD
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  );
  const [activeDevice, setActiveDevice] = useState<SavedDevice | null>(null);

  // Room creation
  const [isAddingRoom, setIsAddingRoom] = useState(false);
  const [newRoomName, setNewRoomName] = useState("");
  const [addRoomError, setAddRoomError] = useState("");
  const addInputRef = useRef<HTMLInputElement>(null);

  // Room deletion
  const [deletingRoom, setDeletingRoom] = useState<Room | null>(null);

  // Property deletion
  const [deletingProperty, setDeletingProperty] = useState(false);

  useEffect(() => {
    if (isAddingRoom) addInputRef.current?.focus();
  }, [isAddingRoom]);

  // Compute device groupings
  const devicesByRoom = savedDevices.reduce<Record<string, SavedDevice[]>>((acc, d) => {
    const key = d.room_id ?? "__unassigned__";
    (acc[key] ??= []).push(d);
    return acc;
  }, {});
  const unassigned = devicesByRoom["__unassigned__"] ?? [];

  // ── Mutations ──────────────────────────────────────────────────────────────

  const assignRoomMut = useMutation({
    mutationFn: ({ deviceId, roomId }: { deviceId: string; roomId: string | null }) =>
      devicesApi.assignRoom(deviceId, roomId),
    onMutate: async ({ deviceId, roomId }) => {
      await queryClient.cancelQueries({ queryKey: ["saved-devices", propertyId] });
      const previous = queryClient.getQueryData<SavedDevice[]>(["saved-devices", propertyId]);
      queryClient.setQueryData<SavedDevice[]>(["saved-devices", propertyId], (old) =>
        old?.map((d) => (d.id === deviceId ? { ...d, room_id: roomId } : d)) ?? [],
      );
      return { previous };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.previous)
        queryClient.setQueryData(["saved-devices", propertyId], ctx.previous);
      toast.error("Failed to move device");
    },
    onSuccess: (_data, { roomId }) => {
      const roomName = roomId
        ? (rooms.find((r) => r.id === roomId)?.name ?? "room")
        : "Unassigned";
      toast.success(`Moved to ${roomName}`);
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["saved-devices", propertyId] }),
  });

  const createRoomMut = useMutation({
    mutationFn: (name: string) => roomsApi.create(propertyId, { name }),
    onSuccess: (room) => {
      queryClient.setQueryData<Room[]>(["rooms", propertyId], (old) => [...(old ?? []), room]);
      setIsAddingRoom(false);
      setNewRoomName("");
      setAddRoomError("");
      toast.success(`Room "${room.name}" created`);
    },
    onError: (err: Error) => {
      if (err.message.includes("409") || err.message.toLowerCase().includes("already exists")) {
        setAddRoomError("A room with that name already exists");
      } else {
        toast.error("Failed to create room");
      }
    },
  });

  const renameRoomMut = useMutation({
    mutationFn: ({ roomId, name }: { roomId: string; name: string }) =>
      roomsApi.rename(roomId, name),
    onSuccess: (updated) => {
      queryClient.setQueryData<Room[]>(["rooms", propertyId], (old) =>
        old?.map((r) => (r.id === updated.id ? updated : r)) ?? [],
      );
      toast.success(`Renamed to "${updated.name}"`);
    },
    onError: (err: Error) => {
      if (err.message.includes("409")) {
        toast.error("A room with that name already exists");
      } else {
        toast.error("Failed to rename room");
      }
    },
  });

  const deleteRoomMut = useMutation({
    mutationFn: (roomId: string) => roomsApi.delete(roomId),
    onSuccess: (_data, roomId) => {
      queryClient.setQueryData<Room[]>(["rooms", propertyId], (old) =>
        old?.filter((r) => r.id !== roomId) ?? [],
      );
      // Move devices that were in this room to null
      queryClient.setQueryData<SavedDevice[]>(["saved-devices", propertyId], (old) =>
        old?.map((d) => (d.room_id === roomId ? { ...d, room_id: null } : d)) ?? [],
      );
      toast.success("Room deleted");
      setDeletingRoom(null);
    },
    onError: () => toast.error("Failed to delete room"),
  });

  const deletePropertyMut = useMutation({
    mutationFn: () => propertiesApi.delete(propertyId),
    onSuccess: () => {
      toast.success("Property deleted");
      router.push("/portfolio");
    },
    onError: () => toast.error("Failed to delete property"),
  });

  // ── DnD handlers ──────────────────────────────────────────────────────────

  function handleDragStart(event: DragStartEvent) {
    const device = savedDevices.find((d) => d.id === event.active.id);
    setActiveDevice(device ?? null);
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    setActiveDevice(null);
    if (!over) return;

    const deviceId = active.id as string;
    const targetRoomId = over.id === "__unassigned__" ? null : (over.id as string);
    const device = savedDevices.find((d) => d.id === deviceId);
    if (!device) return;

    const currentRoomId = device.room_id ?? null;
    if (targetRoomId === currentRoomId) return;

    assignRoomMut.mutate({ deviceId, roomId: targetRoomId });
  }

  // ── Room add form handlers ─────────────────────────────────────────────────

  function handleAddRoom() {
    const name = newRoomName.trim();
    if (!name) return;
    const duplicate = rooms.some((r) => r.name.toLowerCase() === name.toLowerCase());
    if (duplicate) { setAddRoomError("A room with that name already exists"); return; }
    setAddRoomError("");
    createRoomMut.mutate(name);
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  const isEmpty = rooms.length === 0 && unassigned.length === 0;

  return (
    <>
      <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
        <div className="space-y-8">
          {isEmpty && !isAddingRoom ? (
            <div className="py-16 text-center">
              <p className="font-body font-light text-sm text-text-3">
                Add your first room to start organising your devices.
              </p>
            </div>
          ) : (
            <>
              {rooms.map((room) => (
                <RoomSection
                  key={room.id}
                  room={room}
                  devices={devicesByRoom[room.id] ?? []}
                  propertyId={propertyId}
                  onDeleteRequest={setDeletingRoom}
                  onRoomRenamed={(roomId, name) => renameRoomMut.mutate({ roomId, name })}
                />
              ))}
              <UnassignedSection devices={unassigned} propertyId={propertyId} />
            </>
          )}

          {/* Add room form */}
          <div>
            {isAddingRoom ? (
              <div className="flex items-center gap-2">
                <input
                  ref={addInputRef}
                  value={newRoomName}
                  onChange={(e) => { setNewRoomName(e.target.value); setAddRoomError(""); }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleAddRoom();
                    if (e.key === "Escape") { setIsAddingRoom(false); setNewRoomName(""); setAddRoomError(""); }
                  }}
                  placeholder="Room name"
                  className="bg-surface border border-border-strong rounded-lg px-3 py-2 text-sm font-body text-text focus:outline-none focus:border-text-3 w-48"
                />
                <button
                  onClick={handleAddRoom}
                  disabled={createRoomMut.isPending || !newRoomName.trim()}
                  className="bg-graphite text-surface font-body text-sm rounded-lg px-4 py-2 hover:opacity-90 transition-opacity disabled:opacity-40"
                >
                  {createRoomMut.isPending ? "Adding…" : "Add"}
                </button>
                <button
                  onClick={() => { setIsAddingRoom(false); setNewRoomName(""); setAddRoomError(""); }}
                  className="text-text-3 hover:text-text-2 transition-colors"
                >
                  <X size={14} />
                </button>
                {addRoomError && (
                  <span className="font-body font-light text-xs text-red">{addRoomError}</span>
                )}
              </div>
            ) : (
              <button
                onClick={() => setIsAddingRoom(true)}
                className="flex items-center gap-1.5 font-body font-light text-xs text-text-3 hover:text-text-2 transition-colors"
              >
                <Plus size={12} /> Add room
              </button>
            )}
          </div>

          {/* Delete property */}
          <div className="pt-4 border-t border-border">
            <button
              onClick={() => setDeletingProperty(true)}
              className="flex items-center gap-1.5 font-body font-light text-xs text-text-3 hover:text-red transition-colors"
            >
              <Trash2 size={12} /> Delete property
            </button>
          </div>
        </div>

        {/* DragOverlay — follows cursor at 80% opacity */}
        <DragOverlay>
          {activeDevice && (
            <div className="opacity-80 rotate-1 scale-[1.02] pointer-events-none">
              <SavedDeviceCard device={activeDevice} propertyId={propertyId} isDragging />
            </div>
          )}
        </DragOverlay>
      </DndContext>

      {/* Dialogs */}
      <AnimatePresence>
        {deletingRoom && (
          <DeleteRoomDialog
            key="delete-room"
            room={deletingRoom}
            deviceCount={devicesByRoom[deletingRoom.id]?.length ?? 0}
            onConfirm={() => deleteRoomMut.mutate(deletingRoom.id)}
            onCancel={() => setDeletingRoom(null)}
            isPending={deleteRoomMut.isPending}
          />
        )}
        {deletingProperty && (
          <DeletePropertyDialog
            key="delete-property"
            propertyName={propertyName}
            roomCount={rooms.length}
            deviceCount={savedDevices.length}
            onConfirm={() => deletePropertyMut.mutate()}
            onCancel={() => setDeletingProperty(false)}
            isPending={deletePropertyMut.isPending}
          />
        )}
      </AnimatePresence>
    </>
  );
}
