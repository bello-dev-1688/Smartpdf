"""Backend-only development client. No browser/frontend is required."""
import argparse
import json
from pathlib import Path

from pdf_form_filler.services.document_service import DocumentService


def service_for(args):
    return DocumentService(args.storage)


def inspect(args):
    service = service_for(args)
    document_id = args.document_id or service.upload(args.pdf, Path(args.pdf).name)
    print(json.dumps(service.inspect(document_id), indent=2, default=str))
    print(f"\nDocument ID: {document_id}")


def add_field(args):
    service = service_for(args)
    result = service.add_image_field(
        args.document_id, args.field_id, args.page, args.type,
        args.x, args.y, args.width, args.height, args.name
    )
    print(json.dumps(result, indent=2, default=str))


def set_value(args):
    service = service_for(args)
    value = args.value
    if args.type == "checkbox":
        value = value.lower() in {"1", "true", "yes", "on"}
    result = service.set_field_value(args.document_id, args.field_id, value)
    print(json.dumps(result, indent=2, default=str))


def export(args):
    service = service_for(args)
    result = service.export(args.document_id, args.output)
    print(f"Exported: {result}")


parser = argparse.ArgumentParser(description="PDF Form Filler backend development client")
parser.add_argument("--storage", default="data/documents")
sub = parser.add_subparsers(required=True)

p = sub.add_parser("inspect")
p.add_argument("pdf", nargs="?")
p.add_argument("--document-id")
p.set_defaults(fn=inspect)

p = sub.add_parser("add-field")
p.add_argument("document_id")
p.add_argument("field_id")
p.add_argument("--page", type=int, required=True)
p.add_argument("--type", choices=["text", "checkbox", "signature"], required=True)
p.add_argument("--x", type=float, required=True)
p.add_argument("--y", type=float, required=True)
p.add_argument("--width", type=float, required=True)
p.add_argument("--height", type=float, required=True)
p.add_argument("--name")
p.set_defaults(fn=add_field)

p = sub.add_parser("set")
p.add_argument("document_id")
p.add_argument("field_id")
p.add_argument("value")
p.add_argument("--type", choices=["text", "checkbox"], default="text")
p.set_defaults(fn=set_value)

p = sub.add_parser("export")
p.add_argument("document_id")
p.add_argument("output")
p.set_defaults(fn=export)

args = parser.parse_args()
args.fn(args)
